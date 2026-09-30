# ADR-0007: Filtros de período inclusivos e paginação `limit`/`offset`

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O enunciado (§ 2.d) pede filtro do histórico de movimentações por período e/ou
fornecedor. Auditoria de estoque exige precisão de fuso e limites previsíveis
para listagens.

## Decisão

- `data_inicio` e `data_fim` como `datetime` ISO 8601 com offset, inclusivos nas
  duas pontas; `data_inicio > data_fim` → 422.
- Listagens paginadas com `limit`/`offset` (default 20, máximo 100).
- Ordenação fixa e documentada por endpoint (movimentações por `data` desc;
  produtos por `id`).

## Alternativas consideradas

- Datas puras `YYYY-MM-DD` — mais amigáveis, mas obrigariam a decidir o fuso do
  servidor e perderiam precisão dentro do dia.
- Paginação por cursor — mais eficiente para listas enormes, sem necessidade na
  escala da loja e mais difícil de explicar.

## Consequências

- Recortes precisos e previsíveis; o cliente informa o offset explicitamente.
- Listagens grandes ficam limitadas a 100 itens por página.
