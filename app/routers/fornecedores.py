"""Rotas de fornecedores."""

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import SessionDep, exigir_admin
from app.api.openapi import ERRO_422, RESPOSTAS_ESCRITA, RESPOSTAS_LEITURA, resposta
from app.models import Fornecedor
from app.schemas.fornecedor import FornecedorCreate, FornecedorRead, FornecedorUpdate
from app.services import fornecedores

router = APIRouter(prefix="/fornecedores", tags=["fornecedores"])

_EXEMPLO = {
    "id": 1,
    "nome": "Distribuidora Aurora",
    "cnpj": "11222333000181",
    "telefone": "75999990000",
    "email": "contato@aurora.com",
}


@router.post(
    "",
    response_model=FornecedorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_admin)],
    responses={
        **RESPOSTAS_ESCRITA,
        201: resposta("Fornecedor criado", _EXEMPLO),
        409: resposta("CNPJ ou e-mail já cadastrado", {"detail": "CNPJ já cadastrado"}),
        422: ERRO_422,
    },
)
def criar_fornecedor(dados: FornecedorCreate, session: SessionDep) -> Fornecedor:
    """Cria um fornecedor; CNPJ e e-mail precisam ser únicos."""
    return fornecedores.criar(session, dados)


@router.get(
    "",
    response_model=list[FornecedorRead],
    responses={
        **RESPOSTAS_LEITURA,
        200: resposta("Fornecedores paginados", [_EXEMPLO]),
    },
)
def listar_fornecedores(
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    nome: str | None = Query(default=None, description="Filtra por trecho do nome"),
) -> list[Fornecedor]:
    """Lista fornecedores com paginação e filtro opcional por nome."""
    return fornecedores.listar(session, limit=limit, offset=offset, nome=nome)


@router.get(
    "/{fornecedor_id}",
    response_model=FornecedorRead,
    responses={
        **RESPOSTAS_LEITURA,
        200: resposta("Fornecedor encontrado", _EXEMPLO),
        404: resposta("Fornecedor não encontrado", {"detail": "Fornecedor não encontrado"}),
    },
)
def obter_fornecedor(fornecedor_id: int, session: SessionDep) -> Fornecedor:
    """Devolve um fornecedor pelo id."""
    return fornecedores.obter(session, fornecedor_id)


@router.put(
    "/{fornecedor_id}",
    response_model=FornecedorRead,
    dependencies=[Depends(exigir_admin)],
    responses={
        **RESPOSTAS_ESCRITA,
        200: resposta("Fornecedor atualizado", _EXEMPLO),
        404: resposta("Fornecedor não encontrado", {"detail": "Fornecedor não encontrado"}),
        409: resposta("CNPJ ou e-mail já cadastrado", {"detail": "E-mail já cadastrado"}),
        422: ERRO_422,
    },
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
    responses={
        **RESPOSTAS_ESCRITA,
        204: resposta("Fornecedor excluído"),
        404: resposta("Fornecedor não encontrado", {"detail": "Fornecedor não encontrado"}),
        409: resposta(
            "Fornecedor possui produtos vinculados",
            {"detail": "Fornecedor possui produtos vinculados"},
        ),
    },
)
def excluir_fornecedor(fornecedor_id: int, session: SessionDep) -> None:
    """Exclui um fornecedor sem produtos vinculados."""
    fornecedores.excluir(session, fornecedor_id)
