"""Schemas de autenticação."""

from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    """Credenciais enviadas no login."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    """Token de acesso devolvido pelo login."""

    access_token: str
    token_type: str = "bearer"
