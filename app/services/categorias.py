"""Regras de negócio de categorias."""

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.integridade import conflito_de_integridade
from app.models import Categoria, Produto
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate

_MENSAGENS_DE_CONFLITO = {
    "nome": "Categoria já cadastrada",
    "categoria_id": "Categoria possui produtos vinculados",
}


def listar(session: Session, *, limit: int, offset: int) -> list[Categoria]:
    """Lista categorias paginadas."""
    consulta = select(Categoria).order_by(Categoria.id).limit(limit).offset(offset)
    return list(session.scalars(consulta))


def obter(session: Session, categoria_id: int) -> Categoria:
    """Busca uma categoria pelo id ou responde 404."""
    categoria = session.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria não encontrada")
    return categoria


def criar(session: Session, dados: CategoriaCreate) -> Categoria:
    """Cria uma categoria; o nome é único ignorando caixa (§ 2.b)."""
    categoria = Categoria(**dados.model_dump())
    session.add(categoria)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise conflito_de_integridade(exc, _MENSAGENS_DE_CONFLITO) from exc
    session.refresh(categoria)
    return categoria


def atualizar(session: Session, categoria_id: int, dados: CategoriaUpdate) -> Categoria:
    """Renomeia uma categoria; o novo nome também precisa ser único."""
    categoria = obter(session, categoria_id)
    categoria.nome = dados.nome
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise conflito_de_integridade(exc, _MENSAGENS_DE_CONFLITO) from exc
    session.refresh(categoria)
    return categoria


def excluir(session: Session, categoria_id: int) -> None:
    """Exclui categoria vazia; com produtos vinculados responde 409 (§ 2.c)."""
    categoria = obter(session, categoria_id)
    vinculados = session.scalar(
        select(func.count()).select_from(Produto).where(Produto.categoria_id == categoria_id)
    )
    if vinculados:
        raise HTTPException(status.HTTP_409_CONFLICT, "Categoria possui produtos vinculados")

    session.delete(categoria)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise conflito_de_integridade(exc, _MENSAGENS_DE_CONFLITO) from exc
