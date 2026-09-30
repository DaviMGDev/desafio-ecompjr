"""Hash de senha e emissão/validação de tokens de acesso (JWT)."""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

ALGORITMO_JWT = "HS256"

_hasher = PasswordHash.recommended()


def gerar_hash(senha: str) -> str:
    """Gera o hash argon2 da senha — a senha em claro nunca é armazenada."""
    return _hasher.hash(senha)


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Confere a senha contra o hash armazenado."""
    return _hasher.verify(senha, hash_armazenado)


def criar_token(subject: str, perfil: str) -> str:
    """Emite um JWT com o id do usuário em `sub` e o perfil de autorização."""
    expira_em = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "perfil": perfil, "exp": expira_em}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITMO_JWT)


def ler_token(token: str) -> dict:
    """Decodifica e valida o token; levanta `jwt.InvalidTokenError` se inválido."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITMO_JWT])
