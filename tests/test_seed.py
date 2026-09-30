"""Cobre o seed dos usuários e o hash de senha (sem credencial em claro no repo)."""

from app.core.seguranca import verificar_senha
from app.models import PerfilUsuario
from app.services.usuarios import criar_usuario_se_nao_existir, obter_por_email


def test_seed_cria_admin_com_hash(session):
    usuario, criado = criar_usuario_se_nao_existir(
        session,
        nome="Administrador",
        email="Admin@Exemplo.com",
        senha="senha-forte",
        perfil=PerfilUsuario.ADMIN,
    )

    assert criado is True
    assert usuario.perfil is PerfilUsuario.ADMIN
    assert usuario.email == "admin@exemplo.com"
    assert usuario.senha_hash != "senha-forte"
    assert "senha-forte" not in usuario.senha_hash
    assert verificar_senha("senha-forte", usuario.senha_hash)


def test_seed_cria_leitor(session):
    usuario, criado = criar_usuario_se_nao_existir(
        session,
        nome="Leitor",
        email="leitor@exemplo.com",
        senha="senha-leitor",
        perfil=PerfilUsuario.LEITOR,
    )

    assert criado is True
    assert usuario.perfil is PerfilUsuario.LEITOR
    assert verificar_senha("senha-leitor", usuario.senha_hash)


def test_seed_e_idempotente(session):
    primeiro, _ = criar_usuario_se_nao_existir(
        session,
        nome="Administrador",
        email="admin@exemplo.com",
        senha="senha-forte",
        perfil=PerfilUsuario.ADMIN,
    )
    segundo, criado = criar_usuario_se_nao_existir(
        session,
        nome="Outro Nome",
        email="admin@exemplo.com",
        senha="outra-senha",
        perfil=PerfilUsuario.LEITOR,
    )

    assert criado is False
    assert segundo.id == primeiro.id
    assert segundo.perfil is PerfilUsuario.ADMIN
    assert obter_por_email(session, "ADMIN@EXEMPLO.COM") is not None
