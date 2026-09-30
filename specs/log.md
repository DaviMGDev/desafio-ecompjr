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
