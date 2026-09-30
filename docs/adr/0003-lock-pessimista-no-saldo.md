# ADR-0003: Concorrência no saldo com lock pessimista

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O enunciado (§ 3.c, diferencial de 1,0 pt) exige evitar condições de corrida:
duas saídas simultâneas do mesmo produto não podem estourar o saldo nem perder
atualização. Mais de um vendedor ou sistema pode registrar movimentações ao
mesmo tempo.

## Decisão

`POST /movimentacoes` roda em uma transação única:

1. `SELECT ... FOR UPDATE` na linha do produto (lock pessimista);
2. valida o saldo para saídas; insuficiência → 409 e rollback total;
3. insere a movimentação e atualiza `quantidade_em_estoque` (commit único);
4. `CHECK (quantidade_em_estoque >= 0)` no banco como backstop.

O mecanismo é do banco e **independe do modelo de execução (sync ou async)**: com
endpoints sync, o FastAPI processa requisições em threadpool, e a serialização da
seção crítica acontece no lock da linha — a segunda transação espera e relê o
saldo já atualizado (READ COMMITTED).

## Alternativas consideradas

- Lock otimista com coluna de versão — retries e 409 espúrios; mais complexo de
  explicar na defesa.
- `UPDATE` condicional atômico (`WHERE saldo >= quantidade`) — correto, mas menos
  explícito como "mecanismo de bloqueio", que é o que o § 3.c pede.
- Sem lock — perda de atualização: duas saídas leem o mesmo saldo e uma sobrescreve
  a outra.

## Consequências

- Escrita serializada por produto; contenda desprezível na escala de uma loja.
- O teste de concorrência (leaf 4.3, com requisições paralelas reais) comprova o
  comportamento; o trade-off fica pronto para a defesa técnica.
