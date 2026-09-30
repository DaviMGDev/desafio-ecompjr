"""Semeia o usuário administrador a partir de variáveis de ambiente.

Uso: `uv run python -m app.seed` (requer ADMIN_EMAIL e ADMIN_PASSWORD no .env).
"""

from app.core.config import settings
from app.db import SessionLocal
from app.services.usuarios import criar_admin_se_nao_existir


def main() -> int:
    if not settings.admin_email or not settings.admin_password:
        print("Defina ADMIN_EMAIL e ADMIN_PASSWORD no ambiente antes de semear.")
        return 1

    with SessionLocal() as session:
        usuario, criado = criar_admin_se_nao_existir(
            session, settings.admin_email, settings.admin_password
        )

    estado = "criado" if criado else "já existia"
    print(f"Admin {usuario.email}: {estado}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
