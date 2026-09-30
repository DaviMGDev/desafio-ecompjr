"""Cenários de specs/features/movimentacoes.feature: saldo e atomicidade."""

from app.models import Movimentacao


def _criar_produto(client, saldo=0):
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
    produto = client.post(
        "/produtos",
        json={
            "nome": "Produto Um",
            "sku": "SKU-001",
            "preco_custo": "10.00",
            "preco_venda": "15.00",
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    ).json()
    if saldo:
        resposta = client.post(
            "/movimentacoes",
            json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": saldo},
        )
        assert resposta.status_code == 201
    return produto, fornecedor


def test_entrada_soma_ao_saldo_e_data_vem_do_servidor(client):
    produto, _ = _criar_produto(client)

    resposta = client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 3},
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["data"] is not None
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_em_estoque"] == 3


def test_saida_dentro_do_saldo_subtrai(client):
    produto, _ = _criar_produto(client, saldo=5)

    resposta = client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "saida", "quantidade": 2},
    )

    assert resposta.status_code == 201
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_em_estoque"] == 3


def test_saida_maior_que_saldo_falha_sem_deixar_rastro(client):
    produto, _ = _criar_produto(client, saldo=2)

    resposta = client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "saida", "quantidade": 3},
    )

    assert resposta.status_code == 409
    assert "insuficiente" in resposta.json()["detail"]
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_em_estoque"] == 2
    assert len(client.get("/movimentacoes").json()) == 1  # só a entrada inicial


def test_movimentacao_em_produto_inexistente_retorna_404(client):
    resposta = client.post(
        "/movimentacoes",
        json={"produto_id": 999999999, "tipo": "entrada", "quantidade": 1},
    )

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Produto não encontrado"


def test_movimentacao_com_fornecedor_inexistente_retorna_404(client):
    produto, _ = _criar_produto(client)

    resposta = client.post(
        "/movimentacoes",
        json={
            "produto_id": produto["id"],
            "tipo": "entrada",
            "quantidade": 1,
            "fornecedor_id": 999999999,
        },
    )

    assert resposta.status_code == 404


def test_payload_invalido_retorna_422(client):
    produto, _ = _criar_produto(client)

    for corpo in (
        {"produto_id": produto["id"], "tipo": "entrada", "quantidade": 0},
        {"produto_id": produto["id"], "tipo": "saida", "quantidade": -1},
        {"produto_id": produto["id"], "tipo": "transferencia", "quantidade": 1},
    ):
        resposta = client.post("/movimentacoes", json=corpo)
        assert resposta.status_code == 422

    assert len(client.get("/movimentacoes").json()) == 0


def test_fornecedor_e_registrado_na_movimentacao(client, session):
    produto, fornecedor = _criar_produto(client)

    resposta = client.post(
        "/movimentacoes",
        json={
            "produto_id": produto["id"],
            "tipo": "entrada",
            "quantidade": 4,
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["fornecedor_id"] == fornecedor["id"]
    registrada = session.get(Movimentacao, resposta.json()["id"])
    assert registrada is not None
    assert registrada.fornecedor_id == fornecedor["id"]


def test_leitura_de_movimentacao_por_id(client):
    _criar_produto(client, saldo=3)
    movimentacao = client.get("/movimentacoes").json()[0]

    resposta = client.get(f"/movimentacoes/{movimentacao['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == movimentacao["id"]
    assert client.get("/movimentacoes/999999999").status_code == 404


def test_movimentacao_nao_tem_rotas_de_escrita(client):
    _criar_produto(client, saldo=3)
    movimentacao = client.get("/movimentacoes").json()[0]

    assert client.put(f"/movimentacoes/{movimentacao['id']}", json={}).status_code == 405
    assert client.patch(f"/movimentacoes/{movimentacao['id']}", json={}).status_code == 405
    assert client.delete(f"/movimentacoes/{movimentacao['id']}").status_code == 405
    assert client.get(f"/movimentacoes/{movimentacao['id']}").status_code == 200
