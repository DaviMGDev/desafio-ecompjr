"""Cenários de specs/features/consultas.feature — estoque mínimo e filtros."""

from datetime import UTC, datetime

from sqlalchemy import update

from app.models import Movimentacao, Produto


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


def _criar_movimentacao(client, produto_id, tipo, quantidade, fornecedor_id=None):
    corpo = {"produto_id": produto_id, "tipo": tipo, "quantidade": quantidade}
    if fornecedor_id is not None:
        corpo["fornecedor_id"] = fornecedor_id
    return client.post("/movimentacoes", json=corpo).json()


def _mover_data(session, movimentacao_id, quando):
    session.execute(
        update(Movimentacao).where(Movimentacao.id == movimentacao_id).values(data=quando)
    )
    session.commit()


def test_filtro_de_movimentacoes_por_periodo_inclusivo(client, session):
    categoria_id, fornecedor_id = _criar_base(client)
    produto = _criar_produto(client, categoria_id, fornecedor_id, "SKU-A")
    entrada = _criar_movimentacao(client, produto["id"], "entrada", 5)
    saida = _criar_movimentacao(client, produto["id"], "saida", 2)
    _mover_data(session, entrada["id"], datetime(2026, 1, 10, 12, tzinfo=UTC))
    _mover_data(session, saida["id"], datetime(2026, 1, 15, 12, tzinfo=UTC))

    exato = client.get(
        "/movimentacoes",
        params={
            "data_inicio": "2026-01-15T12:00:00+00:00",
            "data_fim": "2026-01-15T12:00:00+00:00",
        },
    )
    assert exato.status_code == 200
    assert [m["id"] for m in exato.json()] == [saida["id"]]

    dia_da_entrada = client.get(
        "/movimentacoes",
        params={
            "data_inicio": "2026-01-10T00:00:00+00:00",
            "data_fim": "2026-01-10T23:59:59+00:00",
        },
    )
    assert [m["id"] for m in dia_da_entrada.json()] == [entrada["id"]]


def test_periodo_invertido_retorna_422(client):
    resposta = client.get(
        "/movimentacoes",
        params={
            "data_inicio": "2026-02-01T00:00:00+00:00",
            "data_fim": "2026-01-01T00:00:00+00:00",
        },
    )

    assert resposta.status_code == 422
    assert "maior" in resposta.json()["detail"]


def test_data_em_formato_invalido_retorna_422(client):
    resposta = client.get("/movimentacoes", params={"data_inicio": "31/01/2026"})

    assert resposta.status_code == 422


def test_filtro_por_fornecedor_tipo_e_combinacao(client, session):
    categoria_id, fornecedor_id = _criar_base(client)
    outro_fornecedor = client.post(
        "/fornecedores",
        json={
            "nome": "Fornecedor Dois",
            "cnpj": "04.252.011/0001-10",
            "telefone": "1",
            "email": "dois@exemplo.com",
        },
    ).json()
    produto = _criar_produto(client, categoria_id, fornecedor_id, "SKU-A")
    entrada_um = _criar_movimentacao(client, produto["id"], "entrada", 5, fornecedor_id)
    entrada_dois = _criar_movimentacao(client, produto["id"], "entrada", 3, outro_fornecedor["id"])
    saida = _criar_movimentacao(client, produto["id"], "saida", 1)
    _mover_data(session, entrada_um["id"], datetime(2026, 1, 10, 12, tzinfo=UTC))
    _mover_data(session, entrada_dois["id"], datetime(2026, 1, 12, 12, tzinfo=UTC))
    _mover_data(session, saida["id"], datetime(2026, 1, 14, 12, tzinfo=UTC))

    so_do_fornecedor = client.get("/movimentacoes", params={"fornecedor_id": fornecedor_id})
    assert [m["id"] for m in so_do_fornecedor.json()] == [entrada_um["id"]]

    combinado_sem_resultado = client.get(
        "/movimentacoes",
        params={
            "fornecedor_id": fornecedor_id,
            "data_inicio": "2026-01-11T00:00:00+00:00",
            "data_fim": "2026-01-13T00:00:00+00:00",
        },
    )
    assert combinado_sem_resultado.json() == []

    so_saidas = client.get("/movimentacoes", params={"tipo": "saida"})
    assert [m["id"] for m in so_saidas.json()] == [saida["id"]]


def test_paginacao_de_movimentacoes(client, session):
    categoria_id, fornecedor_id = _criar_base(client)
    produto = _criar_produto(client, categoria_id, fornecedor_id, "SKU-A")
    movimentacoes = [_criar_movimentacao(client, produto["id"], "entrada", n) for n in (1, 2, 3)]
    for indice, movimentacao in enumerate(movimentacoes, start=1):
        _mover_data(session, movimentacao["id"], datetime(2026, 2, indice, 12, tzinfo=UTC))

    primeira_pagina = client.get("/movimentacoes", params={"limit": 1, "offset": 0})
    segunda_pagina = client.get("/movimentacoes", params={"limit": 1, "offset": 1})

    assert [m["id"] for m in primeira_pagina.json()] == [movimentacoes[2]["id"]]
    assert [m["id"] for m in segunda_pagina.json()] == [movimentacoes[1]["id"]]
