"""Rotas de categorias."""

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import SessionDep, exigir_admin
from app.api.openapi import ERRO_422, RESPOSTAS_ESCRITA, RESPOSTAS_LEITURA, resposta
from app.models import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaRead, CategoriaUpdate
from app.services import categorias

router = APIRouter(prefix="/categorias", tags=["categorias"])

_EXEMPLO = {"id": 1, "nome": "Bebidas"}


@router.post(
    "",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_admin)],
    responses={
        **RESPOSTAS_ESCRITA,
        201: resposta("Categoria criada", _EXEMPLO),
        409: resposta("Categoria já cadastrada", {"detail": "Categoria já cadastrada"}),
        422: ERRO_422,
    },
)
def criar_categoria(dados: CategoriaCreate, session: SessionDep) -> Categoria:
    """Cria uma categoria com nome único (ignorando caixa)."""
    return categorias.criar(session, dados)


@router.get(
    "",
    response_model=list[CategoriaRead],
    responses={
        **RESPOSTAS_LEITURA,
        200: resposta("Categorias paginadas", [_EXEMPLO]),
    },
)
def listar_categorias(
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Categoria]:
    """Lista categorias com paginação."""
    return categorias.listar(session, limit=limit, offset=offset)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaRead,
    responses={
        **RESPOSTAS_LEITURA,
        200: resposta("Categoria encontrada", _EXEMPLO),
        404: resposta("Categoria não encontrada", {"detail": "Categoria não encontrada"}),
    },
)
def obter_categoria(categoria_id: int, session: SessionDep) -> Categoria:
    """Devolve uma categoria pelo id."""
    return categorias.obter(session, categoria_id)


@router.put(
    "/{categoria_id}",
    response_model=CategoriaRead,
    dependencies=[Depends(exigir_admin)],
    responses={
        **RESPOSTAS_ESCRITA,
        200: resposta("Categoria atualizada", _EXEMPLO),
        404: resposta("Categoria não encontrada", {"detail": "Categoria não encontrada"}),
        409: resposta("Categoria já cadastrada", {"detail": "Categoria já cadastrada"}),
        422: ERRO_422,
    },
)
def atualizar_categoria(
    categoria_id: int, dados: CategoriaUpdate, session: SessionDep
) -> Categoria:
    """Renomeia uma categoria; nome repetido responde 409."""
    return categorias.atualizar(session, categoria_id, dados)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(exigir_admin)],
    responses={
        **RESPOSTAS_ESCRITA,
        204: resposta("Categoria excluída"),
        404: resposta("Categoria não encontrada", {"detail": "Categoria não encontrada"}),
        409: resposta(
            "Categoria possui produtos vinculados",
            {"detail": "Categoria possui produtos vinculados"},
        ),
    },
)
def excluir_categoria(categoria_id: int, session: SessionDep) -> None:
    """Exclui uma categoria sem produtos vinculados."""
    categorias.excluir(session, categoria_id)
