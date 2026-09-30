"""Regras de negócio de produtos."""

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.integridade import conflito_de_integridade
from app.models import Categoria, Fornecedor, Movimentacao, Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate

_MENSAGENS_DE_CONFLITO = {
    "sku": "SKU já cadastrado",
    "produto_id": "Produto possui movimentações registradas",
}


def _garantir_referencias(session: Session, categoria_id: int, fornecedor_id: int) -> None:
    """Categoria e fornecedor precisam existir antes de gravar o produto."""
    if session.get(Categoria, categoria_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria não encontrada")
    if session.get(Fornecedor, fornecedor_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fornecedor não encontrado")


def listar(
    session: Session,
    *,
    limit: int,
    offset: int,
    nome: str | None = None,
    categoria_id: int | None = None,
    fornecedor_id: int | None = None,
) -> list[Produto]:
    """Lista produtos paginados, com filtros de nome, categoria e fornecedor."""
    consulta = select(Produto).order_by(Produto.id).limit(limit).offset(offset)
    if nome:
        consulta = consulta.where(Produto.nome.ilike(f"%{nome}%"))
    if categoria_id is not None:
        consulta = consulta.where(Produto.categoria_id == categoria_id)
    if fornecedor_id is not None:
        consulta = consulta.where(Produto.fornecedor_id == fornecedor_id)
    return list(session.scalars(consulta))


def obter(session: Session, produto_id: int) -> Produto:
    """Busca um produto pelo id ou responde 404."""
    produto = session.get(Produto, produto_id)
    if produto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produto não encontrado")
    return produto


def criar(session: Session, dados: ProdutoCreate) -> Produto:
    """Cria um produto; o saldo nasce zerado e só muda por movimentação."""
    _garantir_referencias(session, dados.categoria_id, dados.fornecedor_id)
    produto = Produto(**dados.model_dump())
    session.add(produto)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise conflito_de_integridade(exc, _MENSAGENS_DE_CONFLITO) from exc
    session.refresh(produto)
    return produto


def atualizar(session: Session, produto_id: int, dados: ProdutoUpdate) -> Produto:
    """Atualiza um produto; o saldo não faz parte do payload (ADR-0006)."""
    produto = obter(session, produto_id)
    _garantir_referencias(session, dados.categoria_id, dados.fornecedor_id)
    for campo, valor in dados.model_dump().items():
        setattr(produto, campo, valor)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise conflito_de_integridade(exc, _MENSAGENS_DE_CONFLITO) from exc
    session.refresh(produto)
    return produto


def excluir(session: Session, produto_id: int) -> None:
    """Exclui produto sem movimentações; senão 409 (auditoria, ADR-0005)."""
    produto = obter(session, produto_id)
    movimentacoes = session.scalar(
        select(func.count()).select_from(Movimentacao).where(Movimentacao.produto_id == produto_id)
    )
    if movimentacoes:
        raise HTTPException(status.HTTP_409_CONFLICT, "Produto possui movimentações registradas")

    session.delete(produto)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise conflito_de_integridade(exc, _MENSAGENS_DE_CONFLITO) from exc
