"""Regras de negócio de usuários."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.seguranca import gerar_hash, verificar_senha
from app.models import PerfilUsuario, Usuario


def obter_por_email(session: Session, email: str) -> Usuario | None:
    """Busca usuário pelo e-mail normalizado (sem diferenciar caixa)."""
    return session.scalar(select(Usuario).where(Usuario.email == email.strip().lower()))


def criar_admin_se_nao_existir(session: Session, email: str, senha: str) -> tuple[Usuario, bool]:
    """Cria o admin semeado a partir do ambiente; idempotente.

    Devolve `(usuario, criado)` — sem credenciais no repositório, conforme o
    fluxo de seed documentado no README.
    """
    existente = obter_por_email(session, email)
    if existente is not None:
        return existente, False

    usuario = Usuario(
        nome="Administrador",
        email=email.strip().lower(),
        senha_hash=gerar_hash(senha),
        perfil=PerfilUsuario.ADMIN,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario, True


def autenticar(session: Session, email: str, senha: str) -> Usuario:
    """Confere as credenciais; e-mail inexistente e senha errada têm a mesma resposta."""
    usuario = obter_por_email(session, email)
    if usuario is None or not verificar_senha(senha, usuario.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha inválidos")
    return usuario
