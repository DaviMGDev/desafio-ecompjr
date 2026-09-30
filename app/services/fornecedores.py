"""Regras de negócio de fornecedores."""

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.integridade import conflito_de_integridade
from app.models import Fornecedor, Produto
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate

_MENSAGENS_DE_CONFLITO = {
    "cnpj": "CNPJ já cadastrado",
    "email": "E-mail já cadastrado",
    "fornecedor_id": "Fornecedor possui produtos vinculados",
}


def listar(
    session: Session, *, limit: int, offset: int, nome: str | None = None
) -> list[Fornecedor]:
    """Lista fornecedores paginados, com filtro opcional por trecho do nome."""
    consulta = select(Fornecedor).order_by(Fornecedor.id).limit(limit).offset(offset)
    if nome:
        consulta = consulta.where(Fornecedor.nome.ilike(f"%{nome}%"))
    return list(session.scalars(consulta))


def obter(session: Session, fornecedor_id: int) -> Fornecedor:
    """Busca um fornecedor pelo id ou responde 404."""
    fornecedor = session.get(Fornecedor, fornecedor_id)
    if fornecedor is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fornecedor não encontrado")
    return fornecedor


def criar(session: Session, dados: FornecedorCreate) -> Fornecedor:
    """Cria um fornecedor; CNPJ e e-mail precisam ser únicos."""
    fornecedor = Fornecedor(**dados.model_dump())
    session.add(fornecedor)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise conflito_de_integridade(exc, _MENSAGENS_DE_CONFLITO) from exc
    session.refresh(fornecedor)
    return fornecedor


def atualizar(session: Session, fornecedor_id: int, dados: FornecedorUpdate) -> Fornecedor:
    """Atualiza os dados de um fornecedor existente."""
    fornecedor = obter(session, fornecedor_id)
    for campo, valor in dados.model_dump().items():
        setattr(fornecedor, campo, valor)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise conflito_de_integridade(exc, _MENSAGENS_DE_CONFLITO) from exc
    session.refresh(fornecedor)
    return fornecedor


def excluir(session: Session, fornecedor_id: int) -> None:
    """Exclui um fornecedor; com produtos vinculados responde 409 (ADR-0005)."""
    fornecedor = obter(session, fornecedor_id)
    vinculados = session.scalar(
        select(func.count()).select_from(Produto).where(Produto.fornecedor_id == fornecedor_id)
    )
    if vinculados:
        raise HTTPException(status.HTTP_409_CONFLICT, "Fornecedor possui produtos vinculados")

    session.delete(fornecedor)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise conflito_de_integridade(exc, _MENSAGENS_DE_CONFLITO) from exc
