"""Testes da tela de fornecedores — CRUD, filtro, paginação e perfil leitor."""

from frontend.tests.conftest import HX, gerar_cnpj


def test_lista_vazia_mostra_o_estado_vazio(painel_admin):
    resposta = painel_admin.get("/fornecedores")

    assert resposta.status_code == 200
    assert "Nenhum fornecedor cadastrado" in resposta.text


def test_cria_fornecedor_e_mostra_na_lista(painel_admin, client):
    resposta = painel_admin.post(
        "/fornecedores",
        data={
            "nome": "Distribuidora Aurora",
            "cnpj": "11.222.333/0001-81",
            "telefone": "75999990000",
            "email": "contato@aurora.com",
        },
        headers=HX,
    )

    assert "Fornecedor criado." in resposta.text
    assert "Distribuidora Aurora" in resposta.text
    assert client.get("/fornecedores").json()[0]["cnpj"] == "11222333000181"


def test_cnpj_repetido_mostra_o_detail_do_409(painel_admin, criar_fornecedor):
    criar_fornecedor()

    resposta = painel_admin.post(
        "/fornecedores",
        data={
            "nome": "Aurora Filial",
            "cnpj": "11222333000181",
            "telefone": "75999990001",
            "email": "filial@aurora.com",
        },
        headers=HX,
    )

    assert "CNPJ já cadastrado" in resposta.text


def test_email_repetido_mostra_o_detail_do_409(painel_admin, criar_fornecedor):
    criar_fornecedor()

    resposta = painel_admin.post(
        "/fornecedores",
        data={
            "nome": "Aurora Filial",
            "cnpj": gerar_cnpj(2),
            "telefone": "75999990001",
            "email": "contato@aurora.com",
        },
        headers=HX,
    )

    assert "E-mail já cadastrado" in resposta.text


def test_filtro_por_nome_recorta_a_lista(painel_admin, criar_fornecedor):
    criar_fornecedor()
    criar_fornecedor(nome="Casa do Chá", cnpj=gerar_cnpj(2), email="casa@cha.com")

    resposta = painel_admin.get(
        "/fornecedores/lista?filtro_nome=aurora",
        headers=HX,
    )

    assert "Distribuidora Aurora" in resposta.text
    assert "Casa do Chá" not in resposta.text


def test_editar_preenche_o_formulario(painel_admin, criar_fornecedor):
    fornecedor = criar_fornecedor()

    resposta = painel_admin.get(f"/fornecedores/{fornecedor['id']}/editar", headers=HX)

    assert 'value="Distribuidora Aurora"' in resposta.text
    assert 'value="11222333000181"' in resposta.text
    assert "Editar fornecedor" in resposta.text


def test_atualiza_fornecedor(painel_admin, client, criar_fornecedor):
    fornecedor = criar_fornecedor()

    resposta = painel_admin.post(
        f"/fornecedores/{fornecedor['id']}",
        data={
            "nome": "Aurora Distribuição",
            "cnpj": fornecedor["cnpj"],
            "telefone": fornecedor["telefone"],
            "email": fornecedor["email"],
        },
        headers=HX,
    )

    assert "Fornecedor atualizado." in resposta.text
    assert client.get(f"/fornecedores/{fornecedor['id']}").json()["nome"] == "Aurora Distribuição"


def test_exclui_fornecedor(painel_admin, client, criar_fornecedor):
    fornecedor = criar_fornecedor()

    resposta = painel_admin.post(f"/fornecedores/{fornecedor['id']}/excluir", headers=HX)

    assert "Fornecedor excluído." in resposta.text
    assert client.get(f"/fornecedores/{fornecedor['id']}").status_code == 404


def test_exclusao_com_produto_vinculado_mostra_o_409(painel_admin, criar_fornecedor, criar_produto):
    fornecedor = criar_fornecedor()
    criar_produto(fornecedor_id=fornecedor["id"])

    resposta = painel_admin.post(f"/fornecedores/{fornecedor['id']}/excluir", headers=HX)

    assert "Fornecedor possui produtos vinculados" in resposta.text


def test_carregar_mais_amplia_a_lista(painel_admin, criar_fornecedor):
    for indice in range(21):
        criar_fornecedor(
            nome=f"Fornecedor {indice:02d}",
            cnpj=gerar_cnpj(100 + indice),
            email=f"contato{indice}@exemplo.com",
        )

    primeira = painel_admin.get("/fornecedores")
    assert primeira.text.count('class="item"') == 20
    assert "Carregar mais" in primeira.text

    ampliada = painel_admin.get("/fornecedores/lista?limite=40", headers=HX)
    assert ampliada.text.count('class="item"') == 21
    assert "Carregar mais" not in ampliada.text


def test_leitor_le_a_lista_mas_nao_ve_controles_de_escrita(painel_leitor, criar_fornecedor):
    criar_fornecedor()

    resposta = painel_leitor.get("/fornecedores")

    assert "Distribuidora Aurora" in resposta.text
    assert "Novo fornecedor" not in resposta.text
    assert "Editar" not in resposta.text
    assert "Excluir" not in resposta.text


def test_leitor_forcando_escrita_recebe_403_e_nada_muda(painel_leitor, client, criar_fornecedor):
    fornecedor = criar_fornecedor()

    resposta = painel_leitor.post(f"/fornecedores/{fornecedor['id']}/excluir", headers=HX)

    assert resposta.status_code == 403
    assert "Perfil sem permissão de escrita" in resposta.text
    assert client.get(f"/fornecedores/{fornecedor['id']}").status_code == 200
