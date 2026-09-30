"""Fixtures de banco isoladas por teste e clientes autenticados."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.seguranca import criar_token, gerar_hash
from app.db import engine, get_session
from app.main import app
from app.models import Base, PerfilUsuario, Usuario

# Hashes calculados uma vez por sessão de testes: o argon2 é propositalmente
# lento e recalculá-lo a cada teste dominaria o tempo da suíte.
_HASH_ADMIN = gerar_hash("senha-admin")
_HASH_LEITOR = gerar_hash("senha-leitor")


@pytest.fixture(scope="session")
def _schema():
    """Garante as tabelas antes da suíte, sem depender do estado do banco."""
    Base.metadata.create_all(engine)
    return None


@pytest.fixture()
def session(_schema):
    """Sessão real presa a uma transação externa, revertida ao final do teste."""
    with engine.connect() as connection:
        transacao = connection.begin()
        sessao = Session(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )
        try:
            yield sessao
        finally:
            sessao.close()
            transacao.rollback()


@pytest.fixture()
def _override_sessao(session):
    """Injeta a sessão de teste no lugar da sessão real da aplicação."""
    app.dependency_overrides[get_session] = lambda: session
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_token(session):
    """Token de um admin criado na transação do teste."""
    usuario = Usuario(
        nome="Administrador",
        email="admin@teste.com",
        senha_hash=_HASH_ADMIN,
        perfil=PerfilUsuario.ADMIN,
    )
    session.add(usuario)
    session.commit()
    return criar_token(str(usuario.id), usuario.perfil.value)


@pytest.fixture()
def client(_override_sessao, admin_token):
    """TestClient autenticado como admin — o padrão dos testes de API."""
    with TestClient(app, headers={"Authorization": f"Bearer {admin_token}"}) as test_client:
        yield test_client


@pytest.fixture()
def client_sem_auth(_override_sessao):
    """TestClient sem cabeçalho de autenticação."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def cliente_leitor(session, _override_sessao):
    """TestClient autenticado com perfil de leitura (sem permissão de escrita)."""
    usuario = Usuario(
        nome="Leitor",
        email="leitor@teste.com",
        senha_hash=_HASH_LEITOR,
        perfil=PerfilUsuario.LEITOR,
    )
    session.add(usuario)
    session.commit()

    token = criar_token(str(usuario.id), usuario.perfil.value)
    with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as test_client:
        yield test_client
