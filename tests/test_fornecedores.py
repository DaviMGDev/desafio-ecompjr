"""Cenários de specs/features/fornecedores.feature em testes de API."""

from decimal import Decimal

from app.models import Categoria, Fornecedor, Produto


def _dados(**extra):
    dados = {
        "nome": "Fornecedor Um",
        "cnpj": "11.222.333/0001-81",
        "telefone": "75999990000",
        "email": "fornecedor@exemplo.com",
    }
    dados.update(extra)
    return dados


def test_cria_fornecedor_com_mascara_e_normaliza(client):
    resposta = client.post("/fornecedores", json=_dados())

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id"] > 0
    assert corpo["cnpj"] == "11222333000181"
    assert corpo["email"] == "fornecedor@exemplo.com"


def test_cnpj_duplicado_retorna_409_e_nao_cria(client):
    client.post("/fornecedores", json=_dados())

    resposta = client.post("/fornecedores", json=_dados(email="outro@exemplo.com"))

    assert resposta.status_code == 409
    assert "CNPJ" in resposta.json()["detail"]
    assert len(client.get("/fornecedores").json()) == 1


def test_email_duplicado_retorna_409(client):
    client.post("/fornecedores", json=_dados())

    resposta = client.post(
        "/fornecedores",
        json=_dados(cnpj="04.252.011/0001-10", email="FORNECEDOR@EXEMPLO.COM"),
    )

    assert resposta.status_code == 409
    assert "e-mail" in resposta.json()["detail"].lower()


def test_cnpj_invalido_retorna_422(client):
    resposta = client.post("/fornecedores", json=_dados(cnpj="11111111111111"))

    assert resposta.status_code == 422
    assert isinstance(resposta.json()["detail"], list)


def test_obter_fornecedor_inexistente_retorna_404(client):
    resposta = client.get("/fornecedores/999999999")

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Fornecedor não encontrado"


def test_atualiza_telefone(client):
    criado = client.post("/fornecedores", json=_dados()).json()

    resposta = client.put(f"/fornecedores/{criado['id']}", json=_dados(telefone="75888887777"))

    assert resposta.status_code == 200
    assert resposta.json()["telefone"] == "75888887777"


def test_lista_com_filtro_de_nome(client):
    client.post("/fornecedores", json=_dados(nome="Alfa Distribuidora"))
    client.post(
        "/fornecedores",
        json=_dados(nome="Beta Comércio", cnpj="04.252.011/0001-10", email="beta@exemplo.com"),
    )

    resposta = client.get("/fornecedores", params={"nome": "alfa"})

    assert resposta.status_code == 200
    assert [fornecedor["nome"] for fornecedor in resposta.json()] == ["Alfa Distribuidora"]


def test_exclui_fornecedor_sem_vinculo(client):
    criado = client.post("/fornecedores", json=_dados()).json()

    resposta = client.delete(f"/fornecedores/{criado['id']}")

    assert resposta.status_code == 204
    assert client.get(f"/fornecedores/{criado['id']}").status_code == 404


def test_exclui_fornecedor_com_produto_vinculado_retorna_409(client, session):
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

    resposta = client.delete(f"/fornecedores/{fornecedor.id}")

    assert resposta.status_code == 409
    assert "vinculados" in resposta.json()["detail"]
    assert client.get(f"/fornecedores/{fornecedor.id}").status_code == 200
