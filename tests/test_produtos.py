"""Cenários de specs/features/produtos.feature em testes de API."""

import pytest

from app.models import Movimentacao, TipoMovimentacao


def _criar_base(client):
    categoria = client.post("/categorias", json={"nome": "Bebidas"}).json()
    fornecedor = client.post(
        "/fornecedores",
        json={
            "nome": "Fornecedor Um",
            "cnpj": "11.222.333/0001-81",
            "telefone": "75999990000",
            "email": "fornecedor@exemplo.com",
        },
    ).json()
    return categoria["id"], fornecedor["id"]


def _dados(categoria_id, fornecedor_id, **extra):
    dados = {
        "nome": "Produto Um",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "15.00",
        "categoria_id": categoria_id,
        "fornecedor_id": fornecedor_id,
    }
    dados.update(extra)
    return dados


def test_cria_produto_com_saldo_zero(client):
    categoria_id, fornecedor_id = _criar_base(client)

    resposta = client.post("/produtos", json=_dados(categoria_id, fornecedor_id))

    assert resposta.status_code == 201
    assert resposta.json()["quantidade_em_estoque"] == 0


def test_sku_duplicado_retorna_409(client):
    categoria_id, fornecedor_id = _criar_base(client)
    client.post("/produtos", json=_dados(categoria_id, fornecedor_id))

    resposta = client.post("/produtos", json=_dados(categoria_id, fornecedor_id))

    assert resposta.status_code == 409
    assert "SKU" in resposta.json()["detail"]


def test_saldo_no_payload_de_criacao_retorna_422(client):
    categoria_id, fornecedor_id = _criar_base(client)

    resposta = client.post(
        "/produtos", json=_dados(categoria_id, fornecedor_id, quantidade_em_estoque=10)
    )

    assert resposta.status_code == 422


def test_saldo_no_payload_de_edicao_retorna_422_e_nao_altera(client):
    categoria_id, fornecedor_id = _criar_base(client)
    criado = client.post("/produtos", json=_dados(categoria_id, fornecedor_id)).json()

    resposta = client.put(
        f"/produtos/{criado['id']}",
        json=_dados(categoria_id, fornecedor_id, quantidade_em_estoque=999),
    )

    assert resposta.status_code == 422
    assert client.get(f"/produtos/{criado['id']}").json()["quantidade_em_estoque"] == 0


def test_categoria_inexistente_retorna_404(client):
    _, fornecedor_id = _criar_base(client)

    resposta = client.post("/produtos", json=_dados(999999999, fornecedor_id))

    assert resposta.status_code == 404
    assert "Categoria" in resposta.json()["detail"]


def test_fornecedor_inexistente_retorna_404(client):
    categoria_id, _ = _criar_base(client)

    resposta = client.post("/produtos", json=_dados(categoria_id, 999999999))

    assert resposta.status_code == 404
    assert "Fornecedor" in resposta.json()["detail"]


@pytest.mark.parametrize(
    ("campo", "valor"),
    [("preco_custo", "-1.00"), ("preco_venda", "-1.00"), ("quantidade_minima", -5)],
)
def test_valores_invalidos_retornam_422(client, campo, valor):
    categoria_id, fornecedor_id = _criar_base(client)

    resposta = client.post("/produtos", json=_dados(categoria_id, fornecedor_id, **{campo: valor}))

    assert resposta.status_code == 422


def test_produto_com_movimentacao_nao_pode_ser_excluido(client, session):
    categoria_id, fornecedor_id = _criar_base(client)
    criado = client.post("/produtos", json=_dados(categoria_id, fornecedor_id)).json()
    session.add(Movimentacao(produto_id=criado["id"], tipo=TipoMovimentacao.ENTRADA, quantidade=1))
    session.commit()

    resposta = client.delete(f"/produtos/{criado['id']}")

    assert resposta.status_code == 409
    assert client.get(f"/produtos/{criado['id']}").status_code == 200


def test_produto_sem_movimentacao_pode_ser_excluido(client):
    categoria_id, fornecedor_id = _criar_base(client)
    criado = client.post("/produtos", json=_dados(categoria_id, fornecedor_id)).json()

    resposta = client.delete(f"/produtos/{criado['id']}")

    assert resposta.status_code == 204
    assert client.get(f"/produtos/{criado['id']}").status_code == 404
