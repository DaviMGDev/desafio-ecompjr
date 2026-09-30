# ADR-0012: Testes isolados por savepoint e ordem aleatória

**Data:** 2026-09-30
**Status:** aceito

## Contexto

A suíte precisa ser rápida, independente de ordem de execução e confiável para
defender a regra de concorrência — que exige conexões reais de banco.

## Decisão

- cada teste roda em uma transação externa revertida ao final, com a `Session`
  da aplicação presa a ela (`join_transaction_mode="create_savepoint"`);
- o `TestClient` recebe a sessão de teste por `dependency_overrides`;
- o teste de concorrência abre sessões reais (conexões distintas), dispara as
  requisições em threads com barreira e limpa os dados no `finally`;
- `pytest-randomly` embaralha a ordem dos testes;
- o CI roda lint + migrations + pytest com um serviço PostgreSQL 16.

## Alternativas consideradas

- `TRUNCATE` entre testes — mais lento e mais frágil.
- Testcontainers — um contêiner por sessão de teste; setup extra sem ganho na
  escala do projeto.
- Suíte em ordem fixa — não detecta dependências de ordem.

## Consequências

- Isolamento forte e suíte rápida (~26 s); cada teste enxerga um banco limpo.
- A concorrência tem um teste dedicado com conexões reais e limpeza explícita
  (`tests/test_concorrencia.py`), separado do padrão transacional.
