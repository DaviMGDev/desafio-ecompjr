---
type: index
title: "specs/ — Index"
description: "Registro de nós e ordem de leitura do diretório specs/"
created: "2026-09-30"
updated: "2026-09-30"
---

# specs/ — Index

Status do projeto: active

## Nodes

| Arquivo | Título | Descrição |
|---------|--------|-----------|
| [SPEC.md](SPEC.md) | API de Gerenciamento de Estoque — Specification | Monolito: contexto, pessoas, histórias, arquitetura, dados, API, NFR, stack, ops, decisões |
| [log.md](log.md) | specs/ log | Log de alterações da especificação |
| [features/](features/) | Features BDD | Comportamentos acordados em Gherkin (pt-BR) |
| [DESIGN.md](DESIGN.md) | Sistema visual do painel | Tokens, tipografia, espaçamento e estados (formato DESIGN.md, lint limpo) |
| [layout/](layout/) | Telas do painel (LAYOUT v1) | Uma tela por arquivo `.layout.txt`, estrutura verificada pelo parse check |

## Reading order

`SPEC.md` de cima para baixo; siga os links para as features e para `docs/adr/`.
Para o front-end, `DESIGN.md` (visual) e `layout/` (estrutura das telas) vêm antes
do código.
