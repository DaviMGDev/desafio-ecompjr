"""Configuração do painel — ambiente do processo, separado do da API.

O painel é um serviço à parte (ADR-0014): a URL da API e o segredo da sessão
vivem aqui e no `.env`; o navegador só carrega um cookie de sessão assinado.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DIR_FRONTEND = Path(__file__).resolve().parent
DIR_RAIZ = DIR_FRONTEND.parent
DIR_ESTATICOS = DIR_FRONTEND / "static"


class Settings(BaseSettings):
    """Configurações do front-end (`API_URL`, `SESSION_SECRET`, ...)."""

    model_config = SettingsConfigDict(
        env_file=DIR_RAIZ / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    api_url: str = "http://localhost:8000"
    # Segredo do cookie de sessão (assinatura), separado do JWT_SECRET da API.
    session_secret: str = "dev-apenas-troque-no-env-32-bytes-ou-mais"
    session_cookie: str = "painel_sessao"
    timeout_api: float = 10.0


settings = Settings()
