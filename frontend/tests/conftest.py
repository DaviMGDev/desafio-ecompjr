"""Fixtures dos testes do painel: a API roda em ASGI, sem servidor real.

O `TRANSPORTE` do cliente HTTP do painel é apontado para o app da API
(`app.main`) e a sessão de teste (`_override_sessao`, ADR-0012) continua
valendo — os fluxos de tela exercitam a API de verdade, na mesma transação
revertida ao fim do teste.
"""

import httpx2
import pytest
from fasthtml.common import Client as ClientFastHTML

from app.main import app as app_api
from frontend import api as api_painel
from frontend.main import app as app_painel


class TransporteASGI(httpx2.BaseTransport):
    """Leva as chamadas síncronas do painel ao app ASGI da API (só testes)."""

    def __init__(self, asgi_app):
        self._cliente = ClientFastHTML(asgi_app)

    def handle_request(self, requisicao: httpx2.Request) -> httpx2.Response:
        resposta = getattr(self._cliente, requisicao.method.lower())(
            str(requisicao.url),
            headers=dict(requisicao.headers),
            content=requisicao.content,
        )
        return httpx2.Response(
            resposta.status_code,
            content=resposta.content,
            headers=resposta.headers,
            request=requisicao,
        )


@pytest.fixture()
def transporte(_override_sessao):
    """Aponta as chamadas do painel para a API em ASGI (e devolve ao final)."""
    anterior = api_painel.TRANSPORTE
    api_painel.TRANSPORTE = TransporteASGI(app_api)
    yield
    api_painel.TRANSPORTE = anterior


@pytest.fixture()
def painel(transporte):
    """Cliente do app FastHTML, ainda sem sessão."""
    return ClientFastHTML(app_painel)


@pytest.fixture()
def painel_admin(painel, admin_token):
    """Painel autenticado como admin (o usuário vem da fixture `admin_token`)."""
    resposta = painel.post("/login", data={"email": "admin@teste.com", "senha": "senha-admin"})
    assert resposta.status_code == 303
    return painel


@pytest.fixture()
def painel_leitor(painel, cliente_leitor):
    """Painel autenticado como leitor (a fixture cria o usuário no banco)."""
    resposta = painel.post("/login", data={"email": "leitor@teste.com", "senha": "senha-leitor"})
    assert resposta.status_code == 303
    return painel
