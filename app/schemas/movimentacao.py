"""Schemas de movimentação de estoque (sem edição — registro imutável)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.movimentacao import TipoMovimentacao


class MovimentacaoCreate(BaseModel):
    """Payload de criação de movimentação.

    A `data` é definida pelo servidor e a `quantidade` é sempre positiva; o
    sinal aplicado ao saldo vem do `tipo`.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    produto_id: int
    tipo: TipoMovimentacao
    quantidade: int = Field(gt=0)
    fornecedor_id: int | None = None
    observacao: str | None = Field(default=None, max_length=255)


class MovimentacaoRead(BaseModel):
    """Representação de movimentação devolvida pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    fornecedor_id: int | None
    tipo: TipoMovimentacao
    quantidade: int
    data: datetime
    observacao: str | None
