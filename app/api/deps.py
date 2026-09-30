"""Dependências compartilhadas pelos routers (sessão, usuário autenticado)."""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.seguranca import ler_token
from app.db import get_session
from app.models import PerfilUsuario, Usuario

SessionDep = Annotated[Session, Depends(get_session)]

_bearer = HTTPBearer(auto_error=False)


def usuario_atual(
    session: SessionDep,
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> Usuario:
    """Valida o token Bearer e devolve o usuário autenticado (401 se inválido)."""
    if credenciais is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token de autenticação ausente")

    try:
        payload = ler_token(credenciais.credentials)
        usuario_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido ou expirado") from exc

    usuario = session.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário do token não existe")
    return usuario


def exigir_admin(usuario: Annotated[Usuario, Depends(usuario_atual)]) -> Usuario:
    """Restringe a operação ao perfil de administração (403 caso contrário)."""
    if usuario.perfil is not PerfilUsuario.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Perfil sem permissão de escrita")
    return usuario
