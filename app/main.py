"""Aplicação FastAPI da API de Gerenciamento de Estoque."""

from fastapi import Depends, FastAPI

from app.api.deps import usuario_atual
from app.api.errors import registrar_handlers
from app.api.openapi import resposta
from app.routers import auth as rotas_auth
from app.routers import categorias as rotas_categorias
from app.routers import fornecedores as rotas_fornecedores
from app.routers import movimentacoes as rotas_movimentacoes
from app.routers import produtos as rotas_produtos

app = FastAPI(
    title="API de Gerenciamento de Estoque",
    version="0.1.0",
    description=(
        "API do desafio técnico Prosel 2026.2 (EcompJr/UEFS): fornecedores, "
        "categorias, produtos e movimentações de estoque."
    ),
)

registrar_handlers(app)
app.include_router(rotas_auth.router)
app.include_router(rotas_fornecedores.router, dependencies=[Depends(usuario_atual)])
app.include_router(rotas_categorias.router, dependencies=[Depends(usuario_atual)])
app.include_router(rotas_produtos.router, dependencies=[Depends(usuario_atual)])
app.include_router(rotas_movimentacoes.router, dependencies=[Depends(usuario_atual)])


@app.get(
    "/health",
    tags=["infra"],
    summary="Verifica se a API está no ar",
    responses={200: resposta("API no ar", {"status": "ok"})},
)
def health() -> dict[str, str]:
    """Responde 200 quando a aplicação está pronta para receber requisições."""
    return {"status": "ok"}
