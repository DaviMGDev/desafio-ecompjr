# ADR-0001: Estoque mínimo por produto

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O enunciado (§ 2.d) exige identificar produtos que atingiram o estoque mínimo,
mas § 2.b não define nenhum campo de mínimo. Sem uma fonte para o limiar, a
consulta ficaria arbitrária.

## Decisão

Adicionar `quantidade_minima` (integer `>= 0`, default 0) à entidade Produto. A
consulta de estoque baixo usa `quantidade_em_estoque <= quantidade_minima`.

## Alternativas consideradas

- Parâmetro de query global — o mesmo endpoint responderia coisas diferentes a
  cada chamada, sem um "estoque mínimo" real da loja.
- Campo de mínimo obrigatório, sem default — quebraria produtos já cadastrados.

## Consequências

- Consulta intrínseca e por produto; produtos nascem com mínimo 0 (zerados já
  aparecem como "no mínimo").
- Campo além do mínimo listado em § 2.b — registrado como decisão de projeto no
  `specs/SPEC.md`.
