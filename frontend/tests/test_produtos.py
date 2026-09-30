"""Testes da tela de produtos — CRUD com selects, filtros e perfil leitor."""

from frontend.tests.conftest import HX


def test_lista_vazia_mostra_o_estado_vazio(painel_admin):
    resposta = painel_admin.get("/produtos")

    assert resposta.status_code == 200
    assert "Nenhum produto cadastrado" in resposta.text


def test_cria_produto_com_categoria_e_fornecedor(
    painel_admin, client, criar_categoria, criar_fornecedor
):
    categoria = criar_categoria("Bebidas")
    fornecedor = criar_fornecedor()

    resposta = painel_admin.post(
        "/produtos",
        data={
            "nome": "Chá preto 500g",
            "sku": "CHA-500",
            "preco_custo": "8.50",
            "preco_venda": "14.90",
            "quantidade_minima": "5",
            "categoria_id": str(categoria["id"]),
            "fornecedor_id": str(fornecedor["id"]),
        },
        headers=HX,
    )

    assert "Produto criado." in resposta.text
    assert "Chá preto 500g" in resposta.text
    assert "Bebidas" in resposta.text  # opção do select recarregada

    corpo = client.get("/produtos").json()[0]
    assert corpo["sku"] == "CHA-500"
    assert corpo["quantidade_em_estoque"] == 0
    assert corpo["categoria_id"] == categoria["id"]


def test_sku_repetido_mostra_o_detail_do_409(painel_admin, criar_produto):
    produto = criar_produto()

    resposta = painel_admin.post(
        "/produtos",
        data={
            "nome": "Outro chá",
            "sku": produto["sku"],
            "preco_custo": "1.00",
            "preco_venda": "2.00",
            "quantidade_minima": "0",
            "categoria_id": str(produto["categoria_id"]),
            "fornecedor_id": str(produto["fornecedor_id"]),
        },
        headers=HX,
    )

    assert "SKU já cadastrado" in resposta.text


def test_preco_invalido_mostra_erro_por_campo(painel_admin, criar_produto):
    produto = criar_produto()

    resposta = painel_admin.post(
        "/produtos",
        data={
            "nome": "Chá verde",
            "sku": "CHA-501",
            "preco_custo": "-1",
            "preco_venda": "10.00",
            "quantidade_minima": "0",
            "categoria_id": str(produto["categoria_id"]),
            "fornecedor_id": str(produto["fornecedor_id"]),
        },
        headers=HX,
    )

    assert "campo-com-erro" in resposta.text
    assert "erro-campo" in resposta.text


def test_filtro_por_nome_recorta_a_lista(painel_admin, criar_produto):
    produto = criar_produto(nome="Chá preto 500g", sku="CHA-500")
    criar_produto(
        nome="Caneca esmaltada",
        sku="CAN-1",
        categoria_id=produto["categoria_id"],
        fornecedor_id=produto["fornecedor_id"],
    )

    resposta = painel_admin.get("/produtos/lista?filtro_nome=preto", headers=HX)

    assert "Chá preto 500g" in resposta.text
    assert "Caneca esmaltada" not in resposta.text


def test_editar_preenche_o_formulario(painel_admin, criar_produto):
    produto = criar_produto()

    resposta = painel_admin.get(f"/produtos/{produto['id']}/editar", headers=HX)

    assert 'value="Chá preto 500g"' in resposta.text
    assert 'value="8.50"' in resposta.text
    assert "Editar produto" in resposta.text


def test_atualiza_produto(painel_admin, client, criar_produto):
    produto = criar_produto()

    resposta = painel_admin.post(
        f"/produtos/{produto['id']}",
        data={
            "nome": "Chá preto 1kg",
            "sku": produto["sku"],
            "preco_custo": produto["preco_custo"],
            "preco_venda": "29.90",
            "quantidade_minima": "5",
            "categoria_id": str(produto["categoria_id"]),
            "fornecedor_id": str(produto["fornecedor_id"]),
        },
        headers=HX,
    )

    assert "Produto atualizado." in resposta.text
    corpo = client.get(f"/produtos/{produto['id']}").json()
    assert corpo["nome"] == "Chá preto 1kg"
    assert corpo["quantidade_minima"] == 5
    assert corpo["quantidade_em_estoque"] == 0


def test_exclui_produto(painel_admin, client, criar_produto):
    produto = criar_produto()

    resposta = painel_admin.post(f"/produtos/{produto['id']}/excluir", headers=HX)

    assert "Produto excluído." in resposta.text
    assert client.get(f"/produtos/{produto['id']}").status_code == 404


def test_exclusao_com_movimentacao_mostra_o_409(painel_admin, client, criar_produto):
    produto = criar_produto()
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 1},
    )

    resposta = painel_admin.post(f"/produtos/{produto['id']}/excluir", headers=HX)

    assert "Produto possui movimentações registradas" in resposta.text


def test_saldo_so_muda_por_movimentacao(painel_admin, client, criar_produto):
    produto = criar_produto(quantidade_minima=5)
    client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 3},
    )

    resposta = painel_admin.get("/produtos")

    assert "Estoque: 3" in resposta.text
    assert "Crítico" in resposta.text
    assert 'name="quantidade_em_estoque"' not in resposta.text


def test_leitor_le_a_lista_mas_nao_ve_controles_de_escrita(painel_leitor, criar_produto):
    criar_produto()

    resposta = painel_leitor.get("/produtos")

    assert "Chá preto 500g" in resposta.text
    assert "Novo produto" not in resposta.text
    assert "Editar" not in resposta.text
    assert "Excluir" not in resposta.text


def test_leitor_forcando_escrita_recebe_403_e_nada_muda(painel_leitor, client, criar_produto):
    produto = criar_produto()

    resposta = painel_leitor.post(f"/produtos/{produto['id']}/excluir", headers=HX)

    assert resposta.status_code == 403
    assert "Perfil sem permissão de escrita" in resposta.text
    assert client.get(f"/produtos/{produto['id']}").status_code == 200
