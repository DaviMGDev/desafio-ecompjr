"""Rotas de categorias."""

from fastapi import APIRouter, Query, status

from app.api.deps import SessionDep
from app.models import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaRead, CategoriaUpdate
from app.services import categorias

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.post("", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def criar_categoria(dados: CategoriaCreate, session: SessionDep) -> Categoria:
    """Cria uma categoria com nome único (ignorando caixa)."""
    return categorias.criar(session, dados)


@router.get("", response_model=list[CategoriaRead])
def listar_categorias(
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Categoria]:
    """Lista categorias com paginação."""
    return categorias.listar(session, limit=limit, offset=offset)


@router.get("/{categoria_id}", response_model=CategoriaRead)
def obter_categoria(categoria_id: int, session: SessionDep) -> Categoria:
    """Devolve uma categoria pelo id."""
    return categorias.obter(session, categoria_id)


@router.put("/{categoria_id}", response_model=CategoriaRead)
def atualizar_categoria(
    categoria_id: int, dados: CategoriaUpdate, session: SessionDep
) -> Categoria:
    """Renomeia uma categoria; nome repetido responde 409."""
    return categorias.atualizar(session, categoria_id, dados)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_categoria(categoria_id: int, session: SessionDep) -> None:
    """Exclui uma categoria sem produtos vinculados."""
    categorias.excluir(session, categoria_id)
