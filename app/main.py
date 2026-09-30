"""Aplicação FastAPI da API de Gerenciamento de Estoque."""

from fastapi import FastAPI

from app.api.errors import registrar_handlers
from app.routers import categorias as rotas_categorias
from app.routers import fornecedores as rotas_fornecedores

app = FastAPI(
    title="API de Gerenciamento de Estoque",
    version="0.1.0",
    description=(
        "API do desafio técnico Prosel 2026.2 (EcompJr/UEFS): fornecedores, "
        "categorias, produtos e movimentações de estoque."
    ),
)

registrar_handlers(app)
app.include_router(rotas_fornecedores.router)
app.include_router(rotas_categorias.router)


@app.get("/health", tags=["infra"], summary="Verifica se a API está no ar")
def health() -> dict[str, str]:
    """Responde 200 quando a aplicação está pronta para receber requisições."""
    return {"status": "ok"}
