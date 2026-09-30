"""Fixtures de banco isoladas por teste e clientes autenticados.

A suíte roda num banco próprio (`<DATABASE_URL>_test`, ou `TEST_DATABASE_URL` quando
informado), criado na primeira execução: dados de desenvolvimento/demonstração não
vazam para os testes, e os testes não tocam nesses dados. O banco derivado é
recriado a cada sessão; o informado por variável é respeitado como está.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

import app.db as db
from app.core.config import settings
from app.core.seguranca import criar_token, gerar_hash
from app.db import get_session
from app.main import app
from app.models import Base, PerfilUsuario, Usuario


def _preparar_banco_de_teste() -> tuple[Engine, bool]:
    """Aponta o app para o banco da suíte; devolve `(engine, descartável)`."""
    url = make_url(settings.database_url)
    informada = os.getenv("TEST_DATABASE_URL")
    url_teste = make_url(informada) if informada else url.set(database=f"{url.database}_test")

    if not informada:
        # Cria o banco irmão uma única vez (a conexão de administração precisa
        # de AUTOCOMMIT para rodar o DDL).
        with create_engine(
            url.set(database="postgres"), isolation_level="AUTOCOMMIT"
        ).connect() as conexao:
            existe = conexao.execute(
                text("select 1 from pg_database where datname = :nome"),
                {"nome": url_teste.database},
            ).first()
            if not existe:
                conexao.execute(text(f'create database "{url_teste.database}"'))

    engine_teste = create_engine(url_teste, pool_pre_ping=True)
    db.engine = engine_teste
    db.SessionLocal = sessionmaker(bind=engine_teste, autoflush=False, expire_on_commit=False)
    return engine_teste, informada is None


engine, _BANCO_DESCARTAVEL = _preparar_banco_de_teste()

# Hashes calculados uma vez por sessão de testes: o argon2 é propositalmente
# lento e recalculá-lo a cada teste dominaria o tempo da suíte.
_HASH_ADMIN = gerar_hash("senha-admin")
_HASH_LEITOR = gerar_hash("senha-leitor")


@pytest.fixture(scope="session", autouse=True)
def _schema():
    """Garante as tabelas antes de qualquer teste, sem depender do estado do banco.

    É `autouse` de propósito: testes que falam direto com `SessionLocal` (sem a
    fixture de sessão, como o de concorrência) não podem depender da ordem para
    encontrar o schema criado.
    """
    if _BANCO_DESCARTAVEL:
        # O banco derivado é nosso: recriar as tabelas mantém o schema atual.
        Base.metadata.drop_all(engine)
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
