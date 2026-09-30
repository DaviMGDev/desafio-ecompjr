---
type: log
title: "specs/ log"
description: "Log de atividades do diretório specs/"
created: "2026-09-30"
updated: "2026-09-30"
---

# specs/ log

## 2026-09-30

- Inicialização do `specs/` — API de Gerenciamento de Estoque, status draft.
- Features BDD em `specs/features/` (subdiretório usado porque a preocupação
  cresceu para múltiplos arquivos).
- ADRs ficam em `docs/adr/` (fora de `specs/`) por direção explícita do projeto
  no `AGENTS.md` — desvio do default documentado aqui.
- Implementação concluída a partir deste SPEC: CRUD com erros padronizados,
  movimentações transacionais com lock pessimista (teste de concorrência),
  consultas avançadas, autenticação JWT, suíte de testes, CI e README.
  Decisões registradas em `docs/adr/0001..0013`. Status do projeto: ativo.
- Início do front-end (branch `frontend`): UI FastHTML consumindo a API como
  cliente externo, sem alterar routers/models/services. Questões abertas fechadas
  em lote — Pico CSS, serviço separado em `:5001` com JWT em cookie de sessão,
  dependências em grupo opcional `frontend`, leitor semeado por ambiente,
  paginação "carregar mais", nenhum endpoint novo. Decisões arquiteturais nos
  `docs/adr/0014..0016` (D10–D12 no SPEC).
- `specs/DESIGN.md` (sistema visual do painel, com `design.md lint` limpo) e
  `specs/layout/*.layout.txt` (seis telas, parse check exit 0) — contrato do
  front-end registrado antes do código; a subpasta `layout/` existe porque o
  formato LAYOUT v1 exige um arquivo por tela.
