"""Exemplos de resposta reutilizados na documentação OpenAPI (Swagger)."""

from typing import Any


def resposta(descricao: str, exemplo: Any | None = None) -> dict[str, Any]:
    """Descreve uma resposta; com exemplo, o Swagger mostra o JSON esperado."""
    retorno: dict[str, Any] = {"description": descricao}
    if exemplo is not None:
        retorno["content"] = {"application/json": {"example": exemplo}}
    return retorno


ERRO_422 = resposta(
    "Dados de entrada inválidos",
    {"detail": [{"loc": ["body", "campo"], "msg": "descrição do problema"}]},
)
ERRO_401 = resposta(
    "Token ausente, inválido ou expirado", {"detail": "Token de autenticação ausente"}
)
ERRO_403 = resposta(
    "Perfil sem permissão de escrita", {"detail": "Perfil sem permissão de escrita"}
)

# Respostas comuns herdadas pelos routers: leitura exige token; escrita exige admin.
RESPOSTAS_LEITURA: dict[int | str, dict[str, Any]] = {401: ERRO_401}
RESPOSTAS_ESCRITA: dict[int | str, dict[str, Any]] = {401: ERRO_401, 403: ERRO_403}
