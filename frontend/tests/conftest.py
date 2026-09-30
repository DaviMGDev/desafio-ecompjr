"""Fixtures dos testes do painel: a API roda em ASGI, sem servidor real.

O `TRANSPORTE` do cliente HTTP do painel é apontado para o app da API
(`app.main`) e a sessão de teste (`_override_sessao`, ADR-0012) continua
valendo — os fluxos de tela exercitam a API de verdade, na mesma transação
revertida ao fim do teste.
"""

import httpx2
import pytest
from fasthtml.common import Client as ClientFastHTML

from app.core.validadores import _digito_verificador
from app.main import app as app_api
from frontend import api as api_painel
from frontend.main import app as app_painel

HX = {"HX-Request": "1"}


def gerar_cnpj(raiz: int) -> str:
    """Gera um CNPJ válido a partir de uma raiz de 12 dígitos (dados de teste)."""
    digitos = f"{raiz:012d}"
    if len(set(digitos)) == 1:
        digitos = f"{raiz + 1:012d}"
    primeiro = _digito_verificador(digitos, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    segundo = _digito_verificador(digitos + primeiro, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return digitos + primeiro + segundo


@pytest.fixture()
def criar_categoria(client):
    """Cria uma categoria pela API (como o admin do teste)."""

    def _criar(nome: str = "Bebidas"):
        resposta = client.post("/categorias", json={"nome": nome})
        assert resposta.status_code == 201, resposta.text
        return resposta.json()

    return _criar


@pytest.fixture()
def criar_fornecedor(client):
    """Cria um fornecedor válido pela API (CNPJ com dígitos verificadores)."""

    def _criar(
        nome: str = "Distribuidora Aurora",
        cnpj: str = "11222333000181",
        email: str = "contato@aurora.com",
        telefone: str = "75999990000",
    ):
        resposta = client.post(
            "/fornecedores",
            json={"nome": nome, "cnpj": cnpj, "telefone": telefone, "email": email},
        )
        assert resposta.status_code == 201, resposta.text
        return resposta.json()

    return _criar


@pytest.fixture()
def criar_produto(client, criar_categoria, criar_fornecedor):
    """Cria um produto pela API, com categoria e fornecedor se faltarem."""

    def _criar(
        nome: str = "Chá preto 500g",
        sku: str = "CHA-500",
        preco_custo: str = "8.50",
        preco_venda: str = "14.90",
        quantidade_minima: int = 0,
        categoria_id: int | None = None,
        fornecedor_id: int | None = None,
    ):
        if categoria_id is None:
            categoria_id = criar_categoria()["id"]
        if fornecedor_id is None:
            fornecedor_id = criar_fornecedor()["id"]
        resposta = client.post(
            "/produtos",
            json={
                "nome": nome,
                "sku": sku,
                "preco_custo": preco_custo,
                "preco_venda": preco_venda,
                "quantidade_minima": quantidade_minima,
                "categoria_id": categoria_id,
                "fornecedor_id": fornecedor_id,
            },
        )
        assert resposta.status_code == 201, resposta.text
        return resposta.json()

    return _criar


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
