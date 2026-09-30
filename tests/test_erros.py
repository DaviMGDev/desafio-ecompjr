"""Cobre o envelope de erro e os handlers globais (ADR-0004)."""

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from app.api.errors import registrar_handlers


class _Corpo(BaseModel):
    quantidade: int


def _app_de_teste() -> FastAPI:
    app = FastAPI()
    registrar_handlers(app)

    @app.get("/nao-encontrado")
    def nao_encontrado() -> None:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    @app.get("/conflito")
    def conflito() -> None:
        raise IntegrityError("INSERT ...", {}, Exception("duplicado"))

    @app.get("/falha-interna")
    def falha_interna() -> None:
        raise RuntimeError("detalhe interno sensível")

    @app.post("/validar")
    def validar(corpo: _Corpo) -> dict[str, int]:
        return {"quantidade": corpo.quantidade}

    return app


def test_erro_de_negocio_mantem_o_detail():
    resposta = TestClient(_app_de_teste()).get("/nao-encontrado")

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Fornecedor não encontrado"}


def test_integrity_error_vira_409_no_envelope():
    resposta = TestClient(_app_de_teste()).get("/conflito")

    assert resposta.status_code == 409
    assert set(resposta.json()) == {"detail"}


def test_validacao_vira_422_com_detail_em_lista():
    resposta = TestClient(_app_de_teste()).post("/validar", json={"quantidade": "abc"})

    assert resposta.status_code == 422
    assert isinstance(resposta.json()["detail"], list)


def test_falha_interna_vira_500_generico_sem_stack_trace():
    cliente = TestClient(_app_de_teste(), raise_server_exceptions=False)
    resposta = cliente.get("/falha-interna")

    assert resposta.status_code == 500
    assert resposta.json() == {"detail": "Erro interno do servidor"}
    assert "Traceback" not in resposta.text
    assert "detalhe interno sensível" not in resposta.text
