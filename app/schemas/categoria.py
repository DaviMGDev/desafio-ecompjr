"""Schemas de categoria."""

from pydantic import BaseModel, ConfigDict, Field


class CategoriaBase(BaseModel):
    """Campos comuns de entrada e saída da categoria."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    nome: str = Field(min_length=1, max_length=80)


class CategoriaCreate(CategoriaBase):
    """Payload de criação de categoria."""


class CategoriaUpdate(CategoriaBase):
    """Payload de atualização de categoria."""


class CategoriaRead(CategoriaBase):
    """Representação de categoria devolvida pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
