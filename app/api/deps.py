"""Dependências compartilhadas pelos routers (sessão de banco, usuário atual)."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_session

SessionDep = Annotated[Session, Depends(get_session)]
