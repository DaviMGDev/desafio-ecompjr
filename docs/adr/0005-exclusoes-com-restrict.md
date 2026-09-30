# ADR-0005: Exclusões com `RESTRICT` + 409

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O enunciado (§ 2.c) manda impedir a exclusão de categoria que possui produtos.
Movimentações são auditoria imutável e o produto precisa continuar rastreável;
a mesma lógica de integridade se aplica às demais referências.

## Decisão

Todas as FKs de referência com `ON DELETE RESTRICT`:

- categoria com produtos → 409;
- fornecedor com produtos → 409;
- produto com movimentações → 409;
- sem vínculo → 204.

A aplicação faz a pré-checagem para devolver mensagem clara; a FK é o backstop
contra a corrida residual.

## Alternativas consideradas

- `SET NULL` — deixaria produto órfão de fornecedor e enfraqueceria a auditoria.
- Soft delete — espalharia filtros por todas as consultas; complexidade não
  pedida pelo enunciado.

## Consequências

- Recursos com vínculo tornam-se indeletáveis — comportamento esperado e
  documentado no SPEC.
- Histórico íntegro; mensagens de erro específicas por tipo de vínculo.
