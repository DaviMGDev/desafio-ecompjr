"""Cenários de specs/features/consultas.feature — estoque mínimo e filtros."""

from sqlalchemy import update

from app.models import Produto


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


def _criar_produto(client, categoria_id, fornecedor_id, sku, minimo=0):
    return client.post(
        "/produtos",
        json={
            "nome": f"Produto {sku}",
            "sku": sku,
            "preco_custo": "1.00",
            "preco_venda": "2.00",
            "quantidade_minima": minimo,
            "categoria_id": categoria_id,
            "fornecedor_id": fornecedor_id,
        },
    ).json()


def _ajustar_saldo(session, produto_id, saldo):
    session.execute(
        update(Produto).where(Produto.id == produto_id).values(quantidade_em_estoque=saldo)
    )
    session.commit()


def test_estoque_baixo_traz_no_limite_e_abaixo_ordenado_por_criticidade(client, session):
    categoria_id, fornecedor_id = _criar_base(client)
    no_limite = _criar_produto(client, categoria_id, fornecedor_id, "SKU-A", minimo=3)
    abaixo = _criar_produto(client, categoria_id, fornecedor_id, "SKU-B", minimo=5)
    acima = _criar_produto(client, categoria_id, fornecedor_id, "SKU-C", minimo=2)
    _ajustar_saldo(session, no_limite["id"], 3)
    _ajustar_saldo(session, abaixo["id"], 1)
    _ajustar_saldo(session, acima["id"], 10)

    resposta = client.get("/produtos/estoque-baixo")

    assert resposta.status_code == 200
    assert [produto["id"] for produto in resposta.json()] == [abaixo["id"], no_limite["id"]]
    assert resposta.json()[0]["quantidade_em_estoque"] == 1
    assert resposta.json()[0]["quantidade_minima"] == 5


def test_estoque_baixo_sem_produtos_criticos_retorna_lista_vazia(client):
    resposta = client.get("/produtos/estoque-baixo")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_estoque_baixo_nao_interfere_no_detalhe_por_id(client):
    categoria_id, fornecedor_id = _criar_base(client)
    produto = _criar_produto(client, categoria_id, fornecedor_id, "SKU-A")

    resposta = client.get(f"/produtos/{produto['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == produto["id"]
