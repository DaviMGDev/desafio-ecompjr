"""Fixtures de banco isoladas por teste (transação revertida no final)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import engine, get_session
from app.main import app
from app.models import Base


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
def client(session):
    """TestClient com a sessão de teste injetada (mesma transação do teste)."""
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
