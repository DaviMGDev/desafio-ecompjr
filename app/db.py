"""Engine e sessões do banco.

A sessão chega aos endpoints por dependency injection; commit e rollback são
explícitos nas camadas de serviço, para que a transação seja visível no código.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """Entrega uma sessão por requisição e a fecha ao final."""
    with SessionLocal() as session:
        yield session
