"""Handlers globais de erro: envelope único e sem stack trace (ADR-0004)."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


def registrar_handlers(app: FastAPI) -> None:
    """Garante que toda falha responda no envelope `{"detail": ...}`.

    - validação de schema → 422 (comportamento padrão do FastAPI, detail em lista);
    - `IntegrityError` → 409 (backstop das regras de unicidade/vínculo);
    - exceção não tratada → 500 genérico, com log no servidor e sem detalhes.
    """

    @app.exception_handler(IntegrityError)
    async def conflito_de_integridade(request: Request, exc: IntegrityError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Conflito de integridade de dados"},
        )

    @app.exception_handler(Exception)
    async def erro_interno(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erro interno não tratado em %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Erro interno do servidor"},
        )
