# ADR-0008: Ordem dos diferenciais — concorrência → testes/CI → auth

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O § 3 oferece diferenciais de até +2 pontos (concorrência 1,0; testes/CI 0,5;
autenticação 0,5) e o prazo de entrega é 16/10/2026. O tempo é o recurso mais
escasso.

## Decisão

Implementar os três diferenciais nesta ordem: **concorrência → testes/CI → auth**.
A autenticação é o primeiro corte se o prazo apertar, no formato mínimo: login
com JWT + perfis leitor/admin, usuário semeado por variável de ambiente/migration
e sem rota pública de cadastro.

## Alternativas consideradas

- Apenas testes/CI — entrega folgada, mas abre mão de 1,5 ponto relativamente
  barato.
- Autenticação completa (refresh token, CRUD de usuários) — custo de vários dias
  para 0,5 ponto.

## Consequências

- Prioriza o melhor retorno por esforço; os requisitos obrigatórios vêm antes.
- A entrada da autenticação depende do tempo restante; se entrar, o escopo é o
  mínimo acima.
