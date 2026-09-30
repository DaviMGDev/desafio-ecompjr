"""Cenários de specs/features/categorias.feature em testes de API."""

from decimal import Decimal

import pytest

from app.models import Categoria, Fornecedor, Produto


def test_cria_categoria(client):
    resposta = client.post("/categorias", json={"nome": "Bebidas"})

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Bebidas"


@pytest.mark.parametrize("novo", ["Bebidas", "bebidas"])
def test_nome_duplicado_ignorando_caixa_retorna_409(client, novo):
    client.post("/categorias", json={"nome": "Bebidas"})

    resposta = client.post("/categorias", json={"nome": novo})

    assert resposta.status_code == 409
    assert "cadastrada" in resposta.json()["detail"]


def test_lista_categorias_paginada(client):
    client.post("/categorias", json={"nome": "Bebidas"})
    client.post("/categorias", json={"nome": "Limpeza"})

    resposta = client.get("/categorias", params={"limit": 1, "offset": 1})

    assert resposta.status_code == 200
    assert [categoria["nome"] for categoria in resposta.json()] == ["Limpeza"]


def test_obter_categoria_inexistente_retorna_404(client):
    resposta = client.get("/categorias/999999999")

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Categoria não encontrada"


def test_renomear_para_nome_existente_retorna_409(client):
    bebidas = client.post("/categorias", json={"nome": "Bebidas"}).json()
    limpeza = client.post("/categorias", json={"nome": "Limpeza"}).json()

    resposta = client.put(f"/categorias/{limpeza['id']}", json={"nome": "bebidas"})

    assert resposta.status_code == 409
    assert client.get(f"/categorias/{bebidas['id']}").status_code == 200


def test_exclui_categoria_vazia(client):
    criada = client.post("/categorias", json={"nome": "Papelaria"}).json()

    resposta = client.delete(f"/categorias/{criada['id']}")

    assert resposta.status_code == 204
    assert client.get(f"/categorias/{criada['id']}").status_code == 404


def test_exclui_categoria_com_produto_retorna_409(client, session):
    fornecedor = Fornecedor(
        nome="Fornecedor", cnpj="11222333000181", telefone="1", email="f@exemplo.com"
    )
    categoria = Categoria(nome="Bebidas")
    session.add_all([fornecedor, categoria])
    session.flush()
    session.add(
        Produto(
            nome="Produto",
            sku="SKU-1",
            preco_custo=Decimal("10.00"),
            preco_venda=Decimal("15.00"),
            categoria_id=categoria.id,
            fornecedor_id=fornecedor.id,
        )
    )
    session.commit()

    resposta = client.delete(f"/categorias/{categoria.id}")

    assert resposta.status_code == 409
    assert "vinculados" in resposta.json()["detail"]
    assert client.get(f"/categorias/{categoria.id}").status_code == 200
