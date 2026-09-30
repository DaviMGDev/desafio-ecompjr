"""Testes da tela de estoque baixo — consulta avançada e perfil leitor."""

from frontend.tests.conftest import HX


def test_estoque_baixo_nao_aceita_escrita(painel_admin):
    resposta = painel_admin.post("/estoque-baixo", data={}, headers=HX)

    assert resposta.status_code == 405  # tela somente leitura


def test_lista_vazia_mostra_estado_vazio(painel_admin):
    resposta = painel_admin.get("/estoque-baixo")

    assert resposta.status_code == 200
    assert "Nenhum produto abaixo do mínimo" in resposta.text


def test_mostra_produto_critico_com_saldo_e_atalho(painel_admin, client, criar_produto):
    produto = criar_produto(quantidade_minima=5)
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 2},
    )

    resposta = painel_admin.get("/estoque-baixo")

    assert "Chá preto 500g" in resposta.text
    assert "Estoque: 2" in resposta.text
    assert "Crítico" in resposta.text
    assert f"/movimentacoes?produto_id={produto['id']}" in resposta.text


def test_produto_com_saldo_acima_do_minimo_nao_aparece(painel_admin, client, criar_produto):
    produto = criar_produto(quantidade_minima=5)
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 10},
    )

    resposta = painel_admin.get("/estoque-baixo")

    assert "Chá preto 500g" not in resposta.text
    assert "Nenhum produto abaixo do mínimo" in resposta.text


def test_resumo_conta_os_criticos(painel_admin, criar_produto):
    criar_produto(quantidade_minima=5)

    resposta = painel_admin.get("/estoque-baixo")

    assert "1 produto precisa de reposição" in resposta.text


def test_leitor_nao_ve_o_atalho_de_entrada(painel_leitor, criar_produto):
    criar_produto(quantidade_minima=5)

    resposta = painel_leitor.get("/estoque-baixo")

    assert "Chá preto 500g" in resposta.text
    assert "Registrar entrada" not in resposta.text
