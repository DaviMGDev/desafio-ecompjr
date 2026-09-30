"""Schemas de produto."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    """Campos comuns de entrada e saída do produto.

    `quantidade_em_estoque` não aparece aqui de propósito: o saldo só muda por
    movimentação, então enviá-lo no payload é recusado (extra="forbid" → 422),
    conforme ADR-0006.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    nome: str = Field(min_length=1, max_length=120)
    sku: str = Field(min_length=1, max_length=64)
    preco_custo: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    preco_venda: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    quantidade_minima: int = Field(default=0, ge=0)
    categoria_id: int
    fornecedor_id: int


class ProdutoCreate(ProdutoBase):
    """Payload de criação de produto."""


class ProdutoUpdate(ProdutoBase):
    """Payload de atualização de produto."""


class ProdutoRead(ProdutoBase):
    """Representação de produto devolvida pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    quantidade_em_estoque: int
    data_cadastro: datetime
