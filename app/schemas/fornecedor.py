"""Schemas de fornecedor."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.validadores import normalizar_cnpj


class FornecedorBase(BaseModel):
    """Campos comuns de entrada e saída do fornecedor."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    nome: str = Field(min_length=1, max_length=120)
    cnpj: str
    telefone: str = Field(min_length=1, max_length=20)
    email: EmailStr

    @field_validator("cnpj")
    @classmethod
    def validar_cnpj(cls, valor: str) -> str:
        return normalizar_cnpj(valor)

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        return valor.lower()


class FornecedorCreate(FornecedorBase):
    """Payload de criação de fornecedor."""


class FornecedorUpdate(FornecedorBase):
    """Payload de atualização de fornecedor."""


class FornecedorRead(FornecedorBase):
    """Representação de fornecedor devolvida pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
