"""Semeia os usuários (admin e leitor) a partir do ambiente — ADR-0016.

Uso: `uv run python -m app.seed` (requer `ADMIN_EMAIL`/`ADMIN_PASSWORD` no
`.env`; o leitor é opcional, via `LEITOR_EMAIL`/`LEITOR_PASSWORD`).
"""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import SessionLocal
from app.models import PerfilUsuario
from app.services.usuarios import criar_usuario_se_nao_existir


def _semear(
    session: Session,
    papel: str,
    nome: str,
    email: str | None,
    senha: str | None,
    perfil: PerfilUsuario,
) -> None:
    """Cria um usuário do papel informado, se as variáveis existirem."""
    if not email or not senha:
        print(f"{papel}: pulado (variáveis de ambiente ausentes).")
        return

    _, criado = criar_usuario_se_nao_existir(
        session, nome=nome, email=email, senha=senha, perfil=perfil
    )
    estado = "criado" if criado else "já existia"
    print(f"{papel} {email.strip().lower()}: {estado}.")


def main() -> int:
    """Semeia admin (obrigatório) e leitor (opcional) de forma idempotente."""
    if not settings.admin_email or not settings.admin_password:
        print("Defina ADMIN_EMAIL e ADMIN_PASSWORD no ambiente antes de semear.")
        return 1

    with SessionLocal() as session:
        _semear(
            session,
            "Admin",
            "Administrador",
            settings.admin_email,
            settings.admin_password,
            PerfilUsuario.ADMIN,
        )
        _semear(
            session,
            "Leitor",
            "Leitor",
            settings.leitor_email,
            settings.leitor_password,
            PerfilUsuario.LEITOR,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
