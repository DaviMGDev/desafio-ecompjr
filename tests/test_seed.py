"""Cobre o seed do admin e o hash de senha (sem credencial em claro no repo)."""

from app.core.seguranca import verificar_senha
from app.models import PerfilUsuario
from app.services.usuarios import criar_admin_se_nao_existir, obter_por_email


def test_seed_cria_admin_com_hash(session):
    usuario, criado = criar_admin_se_nao_existir(session, "Admin@Exemplo.com", "senha-forte")

    assert criado is True
    assert usuario.perfil is PerfilUsuario.ADMIN
    assert usuario.email == "admin@exemplo.com"
    assert usuario.senha_hash != "senha-forte"
    assert "senha-forte" not in usuario.senha_hash
    assert verificar_senha("senha-forte", usuario.senha_hash)


def test_seed_e_idempotente(session):
    primeiro, _ = criar_admin_se_nao_existir(session, "admin@exemplo.com", "senha-forte")
    segundo, criado = criar_admin_se_nao_existir(session, "admin@exemplo.com", "outra-senha")

    assert criado is False
    assert segundo.id == primeiro.id
    assert obter_por_email(session, "ADMIN@EXEMPLO.COM") is not None
