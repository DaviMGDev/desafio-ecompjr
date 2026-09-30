"""Modelo de fornecedor."""

from __future__ import annotations

from sqlalchemy import Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Fornecedor(Base):
    """Fornecedor de produtos; CNPJ e e-mail são únicos no banco."""

    __tablename__ = "fornecedores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    cnpj: Mapped[str] = mapped_column(String(14), unique=True)
    telefone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(254))


# Unicidade sem diferenciar caixa; o valor é normalizado na entrada (Pydantic/serviço).
Index("uq_fornecedores_email_lower", func.lower(Fornecedor.email), unique=True)
