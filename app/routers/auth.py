"""Rota de autenticação."""

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.api.openapi import ERRO_422, resposta
from app.core.seguranca import criar_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import usuarios

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        200: resposta(
            "Token emitido",
            {"access_token": "eyJhbGciOiJIUzI1...", "token_type": "bearer"},
        ),
        401: resposta("Credenciais inválidas", {"detail": "E-mail ou senha inválidos"}),
        422: ERRO_422,
    },
)
def login(dados: LoginRequest, session: SessionDep) -> TokenResponse:
    """Autentica e devolve o token JWT com o perfil do usuário."""
    usuario = usuarios.autenticar(session, dados.email, dados.senha)
    return TokenResponse(access_token=criar_token(str(usuario.id), usuario.perfil.value))
