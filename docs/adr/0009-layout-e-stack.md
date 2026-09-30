# ADR-0009: Layout em camadas enxuto, SQLAlchemy sync e Pydantic v2

**Data:** 2026-09-30
**Status:** aceito

## Contexto

A defesa técnica (§ 6) premia o que o candidato consegue explicar em voz alta. A
escala do domínio (uma loja) não exige I/O assíncrono, e a correção sob
concorrência é resolvida no banco (ver ADR-0003).

## Decisão

- Layout em camadas enxuto: `app/main.py`, `app/db.py`, `app/core/`,
  `app/models/`, `app/schemas/`, `app/routers/`, `app/services/`.
- SQLAlchemy 2.x **sync** com psycopg 3; Pydantic v2; Alembic; ruff;
  pytest + httpx; uv (com `requirements.txt` gerado por `uv export`).

## Alternativas consideradas

- DDD cerimonial (camadas adicionais) — cerimônia sem retorno na rubrica nem na
  defesa.
- SQLAlchemy async — mais throughput sob I/O intenso, mas exige driver/engine
  assíncronos e deixa a transação/lock mais difíceis de ler e defender.

## Consequências

- Navegável e defensável; passos pequenos e testáveis.
- **Nenhuma garantia de concorrência depende do modelo sync**: o mecanismo é a
  transação com lock de linha no banco (ADR-0003). Async fica registrado como
  otimização futura, caso o volume de requisições justifique.
