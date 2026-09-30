# ADR-0015: Dependências do frontend em grupo opcional do pyproject raiz

**Data:** 2026-09-30
**Status:** aceito

## Contexto

`requirements.txt` é artefato gerado por `uv export` e é o install usado por quem
avalia a API com `pip`; o CI roda `uv sync --locked`. O frontend precisa de
`python-fasthtml` (o HTMX vem embutido e o Pico CSS acompanha o FastHTML). Onde
declarar essas dependências sem inflar o install avaliado nem criar um segundo
lockfile?

## Decisão

- `python-fasthtml` entra no **grupo opcional `frontend`** do `pyproject.toml` da
  raiz (`[dependency-groups] frontend = [...]`).
- `uv sync` continua instalando só o backend + `dev`; a UI sobe com
  `uv sync --group frontend` (e `uv run --group frontend ...`).
- `uv export --no-hashes -o requirements.txt` segue sem o grupo — grupos não-default
  não entram no export — e o `uv.lock` continua único.
- O CI ganha um segundo job com `--group frontend` para rodar os testes do front.

## Alternativas consideradas

- Dependência raiz simples — um único `uv sync`, mas quem avalia a API via `pip`
  instala FastHTML/HTMX sem usar a UI, e o `requirements.txt` deixa de refletir só
  o serviço avaliado.
- `frontend/pyproject.toml` — footprint do avaliador limpo, mas exige venv separado
  e um lockfile a mais; os testes do front importam `app.main` (ASGITransport), o
  que obrigaria as dependências do backend lá também.

## Consequências

- Um lockfile e um ambiente possível para tudo; `--locked` continua valendo.
- CI com dois jobs: o do backend (inalterado) e o do front (`--group frontend`).
- `requirements.txt` permanece o install mínimo do serviço avaliado.
