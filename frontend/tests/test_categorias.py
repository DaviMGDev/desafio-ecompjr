"""Testes da tela de categorias — lista, CRUD, 409 e perfil leitor."""

from frontend.tests.conftest import HX


def test_lista_vazia_mostra_o_estado_vazio(painel_admin):
    resposta = painel_admin.get("/categorias")

    assert resposta.status_code == 200
    assert "Nenhuma categoria cadastrada" in resposta.text


def test_cria_categoria_e_mostra_na_lista(painel_admin, client):
    resposta = painel_admin.post("/categorias", data={"nome": "Bebidas"}, headers=HX)

    assert resposta.status_code == 200
    assert "Categoria criada." in resposta.text
    assert "Bebidas" in resposta.text
    assert [c["nome"] for c in client.get("/categorias").json()] == ["Bebidas"]


def test_nome_repetido_mostra_o_detail_do_409(painel_admin, criar_categoria):
    criar_categoria("Bebidas")

    resposta = painel_admin.post("/categorias", data={"nome": "bebidas"}, headers=HX)

    assert resposta.status_code == 200
    assert "Categoria já cadastrada" in resposta.text


def test_nome_invalido_mostra_erro_por_campo(painel_admin):
    resposta = painel_admin.post("/categorias", data={"nome": ""}, headers=HX)

    assert "campo-com-erro" in resposta.text
    assert "erro-campo" in resposta.text


def test_editar_preenche_o_formulario(painel_admin, criar_categoria):
    categoria = criar_categoria("Bebidas")

    resposta = painel_admin.get(f"/categorias/{categoria['id']}/editar", headers=HX)

    assert 'value="Bebidas"' in resposta.text
    assert "Editar categoria" in resposta.text


def test_atualiza_categoria(painel_admin, client, criar_categoria):
    categoria = criar_categoria("Bebidas")

    resposta = painel_admin.post(
        f"/categorias/{categoria['id']}", data={"nome": "Bebidas e chás"}, headers=HX
    )

    assert "Categoria atualizada." in resposta.text
    assert client.get(f"/categorias/{categoria['id']}").json()["nome"] == "Bebidas e chás"


def test_exclui_categoria(painel_admin, client, criar_categoria):
    categoria = criar_categoria("Bebidas")

    resposta = painel_admin.post(f"/categorias/{categoria['id']}/excluir", headers=HX)

    assert "Categoria excluída." in resposta.text
    assert client.get(f"/categorias/{categoria['id']}").status_code == 404


def test_exclusao_com_produto_vinculado_mostra_o_409(painel_admin, criar_categoria, criar_produto):
    categoria = criar_categoria("Bebidas")
    criar_produto(categoria_id=categoria["id"])

    resposta = painel_admin.post(f"/categorias/{categoria['id']}/excluir", headers=HX)

    assert "Categoria possui produtos vinculados" in resposta.text


def test_leitor_le_a_lista_mas_nao_ve_controles_de_escrita(painel_leitor, criar_categoria):
    criar_categoria("Bebidas")

    resposta = painel_leitor.get("/categorias")

    assert "Bebidas" in resposta.text
    assert "Nova categoria" not in resposta.text
    assert "Editar" not in resposta.text
    assert "Excluir" not in resposta.text


def test_leitor_forcando_escrita_recebe_403_e_nada_muda(painel_leitor, client, criar_categoria):
    categoria = criar_categoria("Bebidas")

    resposta = painel_leitor.post(f"/categorias/{categoria['id']}/excluir", headers=HX)

    assert resposta.status_code == 403
    assert "Perfil sem permissão de escrita" in resposta.text
    assert client.get(f"/categorias/{categoria['id']}").status_code == 200
