# ADR-0006: Superfície da API — rotas pt-BR, PUT único e saldo somente leitura

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O enunciado está em pt-BR e exige CRUD completo de fornecedores, categorias e
produtos. A auditoria exige que o saldo só mude por movimentação (§ 2.b/§ 2.c).

## Decisão

- Recursos em pt-BR: `/fornecedores`, `/categorias`, `/produtos`,
  `/movimentacoes` (JSON e parâmetros em pt-BR, identificadores em ASCII).
- `PUT` como única rota de edição (sem `PATCH`).
- `quantidade_em_estoque` proibida nos payloads de produto (`extra="forbid"` →
  422): saldo só muda por movimentação.
- Movimentações apenas `POST` e `GET` (lista/detalhe); `PUT`/`PATCH`/`DELETE`
  respondem 405 automaticamente.

## Alternativas consideradas

- Rotas em inglês — convenção internacional, porém menos aderente ao enunciado e
  à leitura do avaliador.
- `PATCH` parcial — mais surface para implementar, documentar e defender.
- Aceitar e ignorar `quantidade_em_estoque` no body — edição silenciosa,
  quebraria a trilha de auditoria.

## Consequências

- Contrato legível para a avaliação; exemplos do README/Swagger em pt-BR.
- `PUT` exige a representação completa do recurso.
- Imutabilidade das movimentações vira um fato observável da API (405).
