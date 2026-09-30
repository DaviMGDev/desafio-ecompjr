"""Rotas de produtos."""

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import SessionDep, exigir_admin
from app.api.openapi import ERRO_422, RESPOSTAS_ESCRITA, RESPOSTAS_LEITURA, resposta
from app.models import Produto
from app.schemas.produto import ProdutoCreate, ProdutoRead, ProdutoUpdate
from app.services import produtos

router = APIRouter(prefix="/produtos", tags=["produtos"])

_EXEMPLO = {
    "id": 1,
    "nome": "Chá preto 500g",
    "sku": "CHA-500",
    "preco_custo": "8.50",
    "preco_venda": "14.90",
    "quantidade_minima": 5,
    "categoria_id": 1,
    "fornecedor_id": 1,
    "quantidade_em_estoque": 10,
    "data_cadastro": "2026-09-30T12:00:00Z",
}
_EXEMPLO_CRITICO = _EXEMPLO | {"quantidade_em_estoque": 3}


@router.post(
    "",
    response_model=ProdutoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_admin)],
    responses={
        **RESPOSTAS_ESCRITA,
        201: resposta("Produto criado", _EXEMPLO),
        404: resposta(
            "Categoria ou fornecedor não encontrado", {"detail": "Categoria não encontrada"}
        ),
        409: resposta("SKU já cadastrado", {"detail": "SKU já cadastrado"}),
        422: ERRO_422,
    },
)
def criar_produto(dados: ProdutoCreate, session: SessionDep) -> Produto:
    """Cria um produto; o saldo nasce zerado e só muda por movimentação."""
    return produtos.criar(session, dados)


@router.get(
    "",
    response_model=list[ProdutoRead],
    responses={
        **RESPOSTAS_LEITURA,
        200: resposta("Produtos paginados", [_EXEMPLO]),
    },
)
def listar_produtos(
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    nome: str | None = Query(default=None, description="Filtra por trecho do nome"),
    categoria_id: int | None = Query(default=None),
    fornecedor_id: int | None = Query(default=None),
) -> list[Produto]:
    """Lista produtos com paginação e filtros de nome, categoria e fornecedor."""
    return produtos.listar(
        session,
        limit=limit,
        offset=offset,
        nome=nome,
        categoria_id=categoria_id,
        fornecedor_id=fornecedor_id,
    )


@router.get(
    "/estoque-baixo",
    response_model=list[ProdutoRead],
    responses={
        **RESPOSTAS_LEITURA,
        200: resposta("Produtos no/abaixo do estoque mínimo", [_EXEMPLO_CRITICO]),
    },
)
def listar_produtos_estoque_baixo(
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Produto]:
    """Produtos com saldo no/abaixo do mínimo, ordenados por criticidade (§ 2.d)."""
    return produtos.listar_estoque_baixo(session, limit=limit, offset=offset)


@router.get(
    "/{produto_id}",
    response_model=ProdutoRead,
    responses={
        **RESPOSTAS_LEITURA,
        200: resposta("Produto encontrado", _EXEMPLO),
        404: resposta("Produto não encontrado", {"detail": "Produto não encontrado"}),
    },
)
def obter_produto(produto_id: int, session: SessionDep) -> Produto:
    """Devolve um produto pelo id."""
    return produtos.obter(session, produto_id)


@router.put(
    "/{produto_id}",
    response_model=ProdutoRead,
    dependencies=[Depends(exigir_admin)],
    responses={
        **RESPOSTAS_ESCRITA,
        200: resposta("Produto atualizado", _EXEMPLO),
        404: resposta(
            "Produto, categoria ou fornecedor não encontrado",
            {"detail": "Produto não encontrado"},
        ),
        409: resposta("SKU já cadastrado", {"detail": "SKU já cadastrado"}),
        422: ERRO_422,
    },
)
def atualizar_produto(produto_id: int, dados: ProdutoUpdate, session: SessionDep) -> Produto:
    """Atualiza um produto; o saldo não é aceito no payload (só movimentação)."""
    return produtos.atualizar(session, produto_id, dados)


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(exigir_admin)],
    responses={
        **RESPOSTAS_ESCRITA,
        204: resposta("Produto excluído"),
        404: resposta("Produto não encontrado", {"detail": "Produto não encontrado"}),
        409: resposta(
            "Produto possui movimentações registradas",
            {"detail": "Produto possui movimentações registradas"},
        ),
    },
)
def excluir_produto(produto_id: int, session: SessionDep) -> None:
    """Exclui um produto sem movimentações registradas."""
    produtos.excluir(session, produto_id)
