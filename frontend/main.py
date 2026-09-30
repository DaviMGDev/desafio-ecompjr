"""App FastHTML do painel de estoque — UI em :5001 consumindo a API (ADR-0014).

Como rodar (com o banco e a API de pé, e o admin semeado):
    uv run --group frontend python -m frontend.main

A sessão e o cliente HTTP ficam em `frontend/sessao.py` e `frontend/api.py`;
cada tela tem seu módulo em `frontend/rotas/`.
"""

from fasthtml.common import Beforeware, Link, Redirect, Script, fast_app, serve

from frontend.componentes import ICONE
from frontend.config import DIR_ESTATICOS, settings
from frontend.rotas import categorias, estoque_baixo, fornecedores, login, movimentacoes, produtos
from frontend.sessao import exigir_login

app, rt = fast_app(
    # Pico e HTMX são servidos do próprio painel (offline-safe), sem CDN.
    pico=False,
    htmx=False,
    surreal=False,
    title="Painel — 愚公移山 Variedades",
    secret_key=settings.session_secret,
    session_cookie=settings.session_cookie,
    static_path=str(DIR_ESTATICOS),
    hdrs=(
        Link(rel="icon", href=ICONE),
        Link(rel="stylesheet", href="/css/pico.min.css"),
        Link(rel="stylesheet", href="/css/app.css"),
        Script(src="/js/htmx.min.js", defer=True),
    ),
    # Tudo exige login, menos a própria tela de login e os estáticos.
    before=Beforeware(
        exigir_login,
        skip=[r"/login", r"/css/.+", r"/js/.+", r"/favicon\.ico"],
    ),
)

for modulo in (login, produtos, estoque_baixo, movimentacoes, fornecedores, categorias):
    modulo.ar.to_app(app)


@rt("/", methods=["GET"])
def raiz():
    """A raiz do painel é a lista de produtos."""
    return Redirect("/produtos")


if __name__ == "__main__":
    # appname explícito para o reload enxergar `frontend.main` a partir da raiz.
    serve(appname="frontend.main")
