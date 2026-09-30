"""Testes do login do painel — credenciais válidas, erro e logout."""


def test_login_exibe_formulario(painel):
    resposta = painel.get("/login")

    assert resposta.status_code == 200
    assert "E-mail" in resposta.text
    assert "Entrar" in resposta.text


def test_raiz_sem_sessao_redireciona_para_login(painel):
    resposta = painel.get("/")

    assert resposta.status_code == 303
    assert resposta.headers["location"] == "/login"


def test_login_com_credenciais_invalidas_mostra_o_detail_da_api(painel):
    resposta = painel.post("/login", data={"email": "admin@teste.com", "senha": "senha-errada"})

    assert resposta.status_code == 200
    assert "E-mail ou senha inválidos" in resposta.text
    assert "alerta-erro" in resposta.text


def test_login_valido_abre_sessao_e_vai_para_produtos(painel, admin_token):
    resposta = painel.post("/login", data={"email": "admin@teste.com", "senha": "senha-admin"})

    assert resposta.status_code == 303
    assert resposta.headers["location"] == "/produtos"
    # a sessão assinada viaja no cookie; o token não vai ao HTML
    assert "access_token" not in resposta.text


def test_login_de_quem_ja_entrou_vai_para_o_painel(painel_admin):
    resposta = painel_admin.get("/login")

    assert resposta.status_code == 303
    assert resposta.headers["location"] == "/produtos"


def test_logout_limpa_a_sessao(painel_admin):
    resposta = painel_admin.post("/logout")

    assert resposta.status_code == 303
    assert resposta.headers["location"] == "/login"
    assert painel_admin.get("/").headers["location"] == "/login"
