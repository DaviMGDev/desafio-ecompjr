"""Traduz conflitos de integridade do banco em erros de negócio legíveis."""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


def conflito_de_integridade(exc: IntegrityError, mensagens: dict[str, str]) -> HTTPException:
    """Mapeia o trecho do nome da constraint violada para uma mensagem pt-BR.

    O nome vem do diagnóstico do driver (PostgreSQL); sem correspondência, a
    resposta é genérica em vez de vazar detalhes do banco (ADR-0004).
    """
    diagnostico = getattr(exc.orig, "diag", None)
    nome = getattr(diagnostico, "constraint_name", None) or ""
    for trecho, mensagem in mensagens.items():
        if trecho in nome:
            return HTTPException(status.HTTP_409_CONFLICT, mensagem)
    return HTTPException(status.HTTP_409_CONFLICT, "Conflito de integridade de dados")
