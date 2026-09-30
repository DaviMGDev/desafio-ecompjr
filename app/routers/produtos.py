"""Rotas de produtos."""

from fastapi import APIRouter, Query, status

from app.api.deps import SessionDep
from app.models import Produto
from app.schemas.produto import ProdutoCreate, ProdutoRead, ProdutoUpdate
from app.services import produtos

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.post("", response_model=ProdutoRead, status_code=status.HTTP_201_CREATED)
def criar_produto(dados: ProdutoCreate, session: SessionDep) -> Produto:
    """Cria um produto; o saldo nasce zerado e só muda por movimentação."""
    return produtos.criar(session, dados)


@router.get("", response_model=list[ProdutoRead])
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


@router.get("/{produto_id}", response_model=ProdutoRead)
def obter_produto(produto_id: int, session: SessionDep) -> Produto:
    """Devolve um produto pelo id."""
    return produtos.obter(session, produto_id)


@router.put("/{produto_id}", response_model=ProdutoRead)
def atualizar_produto(produto_id: int, dados: ProdutoUpdate, session: SessionDep) -> Produto:
    """Atualiza um produto; o saldo não é aceito no payload (só movimentação)."""
    return produtos.atualizar(session, produto_id, dados)


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_produto(produto_id: int, session: SessionDep) -> None:
    """Exclui um produto sem movimentações registradas."""
    produtos.excluir(session, produto_id)
