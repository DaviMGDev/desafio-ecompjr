# ADR-0002: Fornecedor registrado na movimentação

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O enunciado (§ 2.d) pede filtro do histórico de movimentações por fornecedor. O
produto pode trocar de fornecedor ao longo do tempo; derivar o fornecedor do
vínculo atual do produto faria o passado ser reescrito a cada troca.

## Decisão

`fornecedor_id` nullable na tabela `movimentacoes` (FK com `ON DELETE RESTRICT`),
gravado no momento da criação — tipicamente nas entradas. O filtro
`GET /movimentacoes?fornecedor_id=` usa essa coluna.

## Alternativas consideradas

- Derivar de `produto.fornecedor_id` com JOIN — mais simples, mas o histórico
  muda quando o produto troca de fornecedor, quebrando a auditoria.
- Fornecedor obrigatório em toda movimentação — saídas não têm fornecedor
  natural, forçaria um valor sem significado.

## Consequências

- Histórico estável e auditável: a movimentação guarda o fornecedor do dia.
- Coluna adicional; saídas normalmente ficam sem fornecedor e o filtro por
  fornecedor refere-se às movimentações registradas com ele.
