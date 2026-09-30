"""Rotas de movimentações — imutáveis: somente criação e leitura (ADR-0006)."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import SessionDep, exigir_admin
from app.api.openapi import ERRO_422, RESPOSTAS_ESCRITA, RESPOSTAS_LEITURA, resposta
from app.models import Movimentacao, TipoMovimentacao
from app.schemas.movimentacao import MovimentacaoCreate, MovimentacaoRead
from app.services import movimentacoes

router = APIRouter(prefix="/movimentacoes", tags=["movimentacoes"])

_EXEMPLO = {
    "id": 1,
    "produto_id": 1,
    "fornecedor_id": 1,
    "tipo": "entrada",
    "quantidade": 10,
    "data": "2026-09-30T12:00:00Z",
    "observacao": "Reposição de setembro",
}


@router.post(
    "",
    response_model=MovimentacaoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_admin)],
    responses={
        **RESPOSTAS_ESCRITA,
        201: resposta("Movimentação registrada", _EXEMPLO),
        404: resposta("Produto ou fornecedor não encontrado", {"detail": "Produto não encontrado"}),
        409: resposta(
            "Saldo insuficiente para a saída",
            {"detail": "Saldo insuficiente para a saída"},
        ),
        422: ERRO_422,
    },
)
def criar_movimentacao(dados: MovimentacaoCreate, session: SessionDep) -> Movimentacao:
    """Registra entrada/saída e atualiza o saldo na mesma transação."""
    return movimentacoes.criar(session, dados)


@router.get(
    "",
    response_model=list[MovimentacaoRead],
    responses={
        **RESPOSTAS_LEITURA,
        200: resposta("Histórico de movimentações", [_EXEMPLO]),
    },
)
def listar_movimentacoes(
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    produto_id: int | None = Query(default=None),
    tipo: TipoMovimentacao | None = Query(default=None),
    fornecedor_id: int | None = Query(default=None),
    data_inicio: datetime | None = Query(default=None, description="Inclusivo, ISO 8601"),
    data_fim: datetime | None = Query(default=None, description="Inclusivo, ISO 8601"),
) -> list[Movimentacao]:
    """Lista o histórico com filtros de produto, tipo, fornecedor e período."""
    if data_inicio is not None and data_fim is not None and data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="data_inicio não pode ser maior que data_fim",
        )
    return movimentacoes.listar(
        session,
        limit=limit,
        offset=offset,
        produto_id=produto_id,
        tipo=tipo,
        fornecedor_id=fornecedor_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get(
    "/{movimentacao_id}",
    response_model=MovimentacaoRead,
    responses={
        **RESPOSTAS_LEITURA,
        200: resposta("Movimentação encontrada", _EXEMPLO),
        404: resposta("Movimentação não encontrada", {"detail": "Movimentação não encontrada"}),
    },
)
def obter_movimentacao(movimentacao_id: int, session: SessionDep) -> Movimentacao:
    """Devolve uma movimentação pelo id."""
    return movimentacoes.obter(session, movimentacao_id)
