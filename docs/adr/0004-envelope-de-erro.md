# ADR-0004: Envelope de erro `{"detail": ...}`

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O enunciado (§ 2.e) exige modelo de resposta padronizado para exceções, com
código HTTP apropriado, mensagem explicativa, sem stack trace e sem 200 em
requisições falhas.

## Decisão

Envelope único `{"detail": ...}` — string nos erros de negócio, lista de
mensagens no 422 de validação — com handlers globais:

- `RequestValidationError` → 422;
- `IntegrityError` → 409;
- exceção não tratada → 500 genérico (`{"detail": "Erro interno do servidor"}`),
  com log no servidor.

Mapa de status: 422 schema; 404 recurso ou referência ausente; 409 unicidade,
vínculo de exclusão e saldo insuficiente; 400 requisição semanticamente inválida;
500 interno.

## Alternativas consideradas

- Envelope `{"erro": {codigo, mensagem, detalhes}}` — códigos estáveis para
  clientes máquina, mas exige handlers para tudo e diverge do default do FastAPI.
- Default cru do FastAPI — 500 vaza traceback e os formatos variam entre erros.

## Consequências

- Contrato único e alinhado ao Swagger gerado; consumidores leem `detail`.
- Sem taxonomia de códigos de erro (pode ser adicionada depois, com migração de
  contrato).
