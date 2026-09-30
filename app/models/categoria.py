"""Modelo de categoria."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.produto import Produto


class Categoria(Base):
    """Categoria usada para classificar produtos."""

    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80))

    produtos: Mapped[list[Produto]] = relationship(back_populates="categoria")


# Unicidade sem diferenciar caixa; o valor é normalizado na entrada (Pydantic/serviço).
Index("uq_categorias_nome_lower", func.lower(Categoria.nome), unique=True)
