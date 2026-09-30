"""Rotas de movimentações — imutáveis: somente criação e leitura (ADR-0006)."""

from fastapi import APIRouter, Query, status

from app.api.deps import SessionDep
from app.models import Movimentacao
from app.schemas.movimentacao import MovimentacaoCreate, MovimentacaoRead
from app.services import movimentacoes

router = APIRouter(prefix="/movimentacoes", tags=["movimentacoes"])


@router.post("", response_model=MovimentacaoRead, status_code=status.HTTP_201_CREATED)
def criar_movimentacao(dados: MovimentacaoCreate, session: SessionDep) -> Movimentacao:
    """Registra entrada/saída e atualiza o saldo na mesma transação."""
    return movimentacoes.criar(session, dados)


@router.get("", response_model=list[MovimentacaoRead])
def listar_movimentacoes(
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Movimentacao]:
    """Lista o histórico de movimentações, mais recentes primeiro."""
    return movimentacoes.listar(session, limit=limit, offset=offset)


@router.get("/{movimentacao_id}", response_model=MovimentacaoRead)
def obter_movimentacao(movimentacao_id: int, session: SessionDep) -> Movimentacao:
    """Devolve uma movimentação pelo id."""
    return movimentacoes.obter(session, movimentacao_id)
