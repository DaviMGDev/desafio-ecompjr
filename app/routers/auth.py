"""Rota de autenticação."""

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.core.seguranca import criar_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import usuarios

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, session: SessionDep) -> TokenResponse:
    """Autentica e devolve o token JWT com o perfil do usuário."""
    usuario = usuarios.autenticar(session, dados.email, dados.senha)
    return TokenResponse(access_token=criar_token(str(usuario.id), usuario.perfil.value))
