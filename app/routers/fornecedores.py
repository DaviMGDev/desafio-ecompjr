"""Rotas de fornecedores."""

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import SessionDep, exigir_admin
from app.models import Fornecedor
from app.schemas.fornecedor import FornecedorCreate, FornecedorRead, FornecedorUpdate
from app.services import fornecedores

router = APIRouter(prefix="/fornecedores", tags=["fornecedores"])


@router.post(
    "",
    response_model=FornecedorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_admin)],
)
def criar_fornecedor(dados: FornecedorCreate, session: SessionDep) -> Fornecedor:
    """Cria um fornecedor; CNPJ e e-mail precisam ser únicos."""
    return fornecedores.criar(session, dados)


@router.get("", response_model=list[FornecedorRead])
def listar_fornecedores(
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    nome: str | None = Query(default=None, description="Filtra por trecho do nome"),
) -> list[Fornecedor]:
    """Lista fornecedores com paginação e filtro opcional por nome."""
    return fornecedores.listar(session, limit=limit, offset=offset, nome=nome)


@router.get("/{fornecedor_id}", response_model=FornecedorRead)
def obter_fornecedor(fornecedor_id: int, session: SessionDep) -> Fornecedor:
    """Devolve um fornecedor pelo id."""
    return fornecedores.obter(session, fornecedor_id)


@router.put(
    "/{fornecedor_id}",
    response_model=FornecedorRead,
    dependencies=[Depends(exigir_admin)],
)
def atualizar_fornecedor(
    fornecedor_id: int, dados: FornecedorUpdate, session: SessionDep
) -> Fornecedor:
    """Atualiza um fornecedor; unicidade de CNPJ/e-mail continua valendo."""
    return fornecedores.atualizar(session, fornecedor_id, dados)


@router.delete(
    "/{fornecedor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(exigir_admin)],
)
def excluir_fornecedor(fornecedor_id: int, session: SessionDep) -> None:
    """Exclui um fornecedor sem produtos vinculados."""
    fornecedores.excluir(session, fornecedor_id)
