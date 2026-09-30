"""Modelo de movimentação de estoque (registro imutável de auditoria)."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.fornecedor import Fornecedor
    from app.models.produto import Produto


class TipoMovimentacao(enum.StrEnum):
    """Tipo da movimentação; o sinal aplicado ao saldo vem daqui."""

    ENTRADA = "entrada"
    SAIDA = "saida"


class Movimentacao(Base):
    """Entrada ou saída de estoque; imutável pela API (ADR-0006)."""

    __tablename__ = "movimentacoes"
    __table_args__ = (CheckConstraint("quantidade > 0", name="quantidade_positiva"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id", ondelete="RESTRICT"))
    # Gravado na criação para o filtro por fornecedor não ser reescrito pela
    # troca de fornecedor do produto (ADR-0002).
    fornecedor_id: Mapped[int | None] = mapped_column(
        ForeignKey("fornecedores.id", ondelete="RESTRICT"), nullable=True
    )
    tipo: Mapped[TipoMovimentacao] = mapped_column(
        Enum(
            TipoMovimentacao,
            name="tipo_movimentacao",
            values_callable=lambda enum_cls: [membro.value for membro in enum_cls],
        )
    )
    quantidade: Mapped[int]
    data: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    observacao: Mapped[str | None] = mapped_column(String(255), nullable=True)

    produto: Mapped[Produto] = relationship(back_populates="movimentacoes")
    fornecedor: Mapped[Fornecedor | None] = relationship()
