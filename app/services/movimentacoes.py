"""Regras de negócio de movimentações de estoque."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.integridade import conflito_de_integridade
from app.models import Fornecedor, Movimentacao, Produto, TipoMovimentacao
from app.schemas.movimentacao import MovimentacaoCreate

_MENSAGENS_DE_CONFLITO = {"produto_id": "Movimentação inválida para o produto"}


def listar(session: Session, *, limit: int, offset: int) -> list[Movimentacao]:
    """Lista o histórico, mais recente primeiro."""
    consulta = (
        select(Movimentacao)
        .order_by(Movimentacao.data.desc(), Movimentacao.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(consulta))


def obter(session: Session, movimentacao_id: int) -> Movimentacao:
    """Busca uma movimentação pelo id ou responde 404."""
    movimentacao = session.get(Movimentacao, movimentacao_id)
    if movimentacao is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Movimentação não encontrada")
    return movimentacao


def criar(session: Session, dados: MovimentacaoCreate) -> Movimentacao:
    """Insere a movimentação e atualiza o saldo na MESMA transação (ADR-0003).

    O `SELECT ... FOR UPDATE` serializa a seção crítica por produto: a segunda
    transação espera o lock e relê o saldo já atualizado, evitando que duas
    saídas simultâneas estourem o estoque ou percam atualização.
    """
    produto = session.execute(
        select(Produto).where(Produto.id == dados.produto_id).with_for_update()
    ).scalar_one_or_none()
    if produto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produto não encontrado")

    if dados.fornecedor_id is not None and session.get(Fornecedor, dados.fornecedor_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fornecedor não encontrado")

    if dados.tipo is TipoMovimentacao.SAIDA and produto.quantidade_em_estoque < dados.quantidade:
        raise HTTPException(status.HTTP_409_CONFLICT, "Saldo insuficiente para a saída")

    movimentacao = Movimentacao(**dados.model_dump())
    session.add(movimentacao)
    if dados.tipo is TipoMovimentacao.ENTRADA:
        produto.quantidade_em_estoque += dados.quantidade
    else:
        produto.quantidade_em_estoque -= dados.quantidade

    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise conflito_de_integridade(exc, _MENSAGENS_DE_CONFLITO) from exc
    session.refresh(movimentacao)
    return movimentacao
