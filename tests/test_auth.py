"""Cenários de specs/features/autenticacao.feature — login e token."""

from app.core.seguranca import ler_token
from app.models import PerfilUsuario
from app.services.usuarios import criar_admin_se_nao_existir


def test_login_com_credenciais_validas_retorna_token_com_perfil(client, session):
    usuario, _ = criar_admin_se_nao_existir(session, "admin@exemplo.com", "senha-forte")

    resposta = client.post(
        "/auth/login", json={"email": "admin@exemplo.com", "senha": "senha-forte"}
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    payload = ler_token(corpo["access_token"])
    assert payload["sub"] == str(usuario.id)
    assert payload["perfil"] == PerfilUsuario.ADMIN.value


def test_login_com_senha_incorreta_retorna_401(client, session):
    criar_admin_se_nao_existir(session, "admin@exemplo.com", "senha-forte")

    resposta = client.post(
        "/auth/login", json={"email": "admin@exemplo.com", "senha": "senha-errada"}
    )

    assert resposta.status_code == 401
    assert "inválidos" in resposta.json()["detail"]


def test_login_com_email_inexistente_retorna_401(client):
    resposta = client.post(
        "/auth/login", json={"email": "ninguem@exemplo.com", "senha": "qualquer"}
    )

    assert resposta.status_code == 401


def test_login_com_payload_invalido_retorna_422(client):
    resposta = client.post("/auth/login", json={"email": "não-é-email", "senha": "x"})

    assert resposta.status_code == 422
