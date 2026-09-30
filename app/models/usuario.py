"""Modelo de usuário da API."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PerfilUsuario(enum.StrEnum):
    """Perfis de autorização: leitura e administração (ADR-0008)."""

    LEITOR = "leitor"
    ADMIN = "admin"


class Usuario(Base):
    """Usuário autenticável; a senha é armazenada apenas como hash."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[PerfilUsuario] = mapped_column(
        Enum(
            PerfilUsuario,
            name="perfil_usuario",
            values_callable=lambda enum_cls: [membro.value for membro in enum_cls],
        )
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
