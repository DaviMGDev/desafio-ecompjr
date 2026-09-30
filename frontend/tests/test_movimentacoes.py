"""Testes da tela de movimentações — registro, histórico, filtros e perfil."""

from datetime import date, timedelta

from frontend.tests.conftest import HX


def test_historico_vazio(painel_admin):
    resposta = painel_admin.get("/movimentacoes")

    assert resposta.status_code == 200
    assert "Nenhuma movimentação no período" in resposta.text


def test_registra_entrada_e_mostra_o_saldo_atualizado(painel_admin, client, criar_produto):
    produto = criar_produto()

    resposta = painel_admin.post(
        "/movimentacoes",
        data={"produto_id": str(produto["id"]), "tipo": "entrada", "quantidade": "10"},
        headers=HX,
    )

    assert "Movimentação registrada; saldo atualizado." in resposta.text
    assert "Saldo atual: 10" in resposta.text
    assert "Chá preto 500g" in resposta.text
    assert "selo-entrada" in resposta.text
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_em_estoque"] == 10


def test_registra_saida_com_observacao(painel_admin, client, criar_produto):
    produto = criar_produto()
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 10},
    )

    resposta = painel_admin.post(
        "/movimentacoes",
        data={
            "produto_id": str(produto["id"]),
            "tipo": "saida",
            "quantidade": "4",
            "observacao": "Venda no balcão",
        },
        headers=HX,
    )

    assert "Saldo atual: 6" in resposta.text
    assert "selo-saida" in resposta.text
    assert "Venda no balcão" in resposta.text
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_em_estoque"] == 6


def test_saida_sem_saldo_mostra_o_409_e_nao_altera_nada(painel_admin, client, criar_produto):
    produto = criar_produto()
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 2},
    )

    resposta = painel_admin.post(
        "/movimentacoes",
        data={"produto_id": str(produto["id"]), "tipo": "saida", "quantidade": "5"},
        headers=HX,
    )

    assert "Saldo insuficiente para a saída" in resposta.text
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_em_estoque"] == 2


def test_quantidade_zerada_mostra_erro_por_campo(painel_admin, criar_produto):
    produto = criar_produto()

    resposta = painel_admin.post(
        "/movimentacoes",
        data={"produto_id": str(produto["id"]), "tipo": "entrada", "quantidade": "0"},
        headers=HX,
    )

    assert "campo-com-erro" in resposta.text
    assert "erro-campo" in resposta.text


def test_filtro_por_tipo(painel_admin, client, criar_produto):
    produto = criar_produto()
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 10},
    )
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "saida", "quantidade": 4},
    )

    resposta = painel_admin.get("/movimentacoes/lista?filtro_tipo=saida", headers=HX)

    assert "selo-saida" in resposta.text
    assert "selo-entrada" not in resposta.text


def test_filtro_por_periodo_inclusivo(painel_admin, client, criar_produto):
    produto = criar_produto()
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 1},
    )

    ontem = (date.today() - timedelta(days=1)).isoformat()
    amanha = (date.today() + timedelta(days=1)).isoformat()
    resposta = painel_admin.get(
        f"/movimentacoes/lista?filtro_data_inicio={ontem}&filtro_data_fim={amanha}",
        headers=HX,
    )

    assert "selo-entrada" in resposta.text


def test_filtro_por_periodo_futuro_nao_encontra(painel_admin, client, criar_produto):
    produto = criar_produto()
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 1},
    )

    resposta = painel_admin.get("/movimentacoes/lista?filtro_data_inicio=2099-01-01", headers=HX)

    assert "Nenhuma movimentação no período" in resposta.text


def test_periodo_invertido_mostra_o_detail_dim(painel_admin):
    resposta = painel_admin.get(
        "/movimentacoes/lista?filtro_data_inicio=2026-10-02&filtro_data_fim=2026-10-01",
        headers=HX,
    )

    assert "data_inicio não pode ser maior que data_fim" in resposta.text


def test_produto_pre_selecionado_mostra_o_saldo(painel_admin, client, criar_produto):
    produto = criar_produto()
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 7},
    )

    resposta = painel_admin.get(f"/movimentacoes?produto_id={produto['id']}")

    assert "Saldo atual: 7" in resposta.text
    assert f'value="{produto["id"]}"' in resposta.text


def test_saldo_do_produto_atualiza_na_troca(painel_admin, client, criar_produto):
    produto = criar_produto()
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 4},
    )

    resposta = painel_admin.get(f"/movimentacoes/saldo?produto_id={produto['id']}", headers=HX)

    assert "Saldo atual: 4" in resposta.text


def test_leitor_nao_ve_o_formulario_nem_escreve(painel_leitor, client, criar_produto):
    produto = criar_produto()

    resposta = painel_leitor.get("/movimentacoes")

    assert "Registrar movimentação" not in resposta.text
    assert "Histórico" in resposta.text

    forjado = painel_leitor.post(
        "/movimentacoes",
        data={"produto_id": str(produto["id"]), "tipo": "entrada", "quantidade": "5"},
        headers=HX,
    )

    assert forjado.status_code == 403
    assert "Perfil sem permissão de escrita" in forjado.text
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_em_estoque"] == 0


def test_historico_nao_oferece_edicao_ou_exclusao(painel_admin, client, criar_produto):
    produto = criar_produto()
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 1},
    )

    resposta = painel_admin.get("/movimentacoes")

    assert "selo-entrada" in resposta.text
    assert "Editar" not in resposta.text
    assert "Excluir" not in resposta.text
