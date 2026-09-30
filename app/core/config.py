"""Configuração da aplicação, carregada de variáveis de ambiente."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações vindas do ambiente (`.env` em desenvolvimento)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://estoque:estoque@localhost:5432/estoque"
    # Valor de desenvolvimento; em produção o segredo real vem do ambiente.
    jwt_secret: str = "dev-apenas-troque-no-env"
    jwt_expire_minutes: int = 60
    # Admin semeado por `python -m app.seed`; sem credenciais reais no repo.
    admin_email: str | None = None
    admin_password: str | None = None


settings = Settings()
