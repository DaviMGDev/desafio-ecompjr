"""Modelo de produto."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.categoria import Categoria
    from app.models.fornecedor import Fornecedor
    from app.models.movimentacao import Movimentacao


class Produto(Base):
    """Produto do catálogo.

    `quantidade_em_estoque` é denormalizada e só muda por movimentação
    (ADR-0006); o CHECK no banco é o backstop do invariante de saldo (ADR-0003).
    """

    __tablename__ = "produtos"
    __table_args__ = (
        CheckConstraint("preco_custo >= 0", name="preco_custo_nao_negativo"),
        CheckConstraint("preco_venda >= 0", name="preco_venda_nao_negativo"),
        CheckConstraint("quantidade_em_estoque >= 0", name="saldo_nao_negativo"),
        CheckConstraint("quantidade_minima >= 0", name="minimo_nao_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    sku: Mapped[str] = mapped_column(String(64), unique=True)
    preco_custo: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    preco_venda: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    quantidade_em_estoque: Mapped[int] = mapped_column(server_default=text("0"))
    quantidade_minima: Mapped[int] = mapped_column(server_default=text("0"))
    data_cadastro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id", ondelete="RESTRICT"))
    fornecedor_id: Mapped[int] = mapped_column(ForeignKey("fornecedores.id", ondelete="RESTRICT"))

    categoria: Mapped[Categoria] = relationship(back_populates="produtos")
    fornecedor: Mapped[Fornecedor] = relationship()
    movimentacoes: Mapped[list[Movimentacao]] = relationship(back_populates="produto")
