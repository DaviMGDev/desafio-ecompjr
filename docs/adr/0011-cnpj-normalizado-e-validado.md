# ADR-0011: CNPJ normalizado e validado na borda

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O CNPJ chega com ou sem máscara e a unicidade no banco não pode depender do
formato enviado. O enunciado (§ 2.b) pede apenas o campo único, sem definir
normalização.

## Decisão

Normalizar e validar na borda: o schema Pydantic remove caracteres não numéricos,
confere os dígitos verificadores e devolve 14 dígitos; o banco armazena
`char(14)` sem máscara com `UNIQUE` simples.

## Alternativas consideradas

- Armazenar como recebido — unicidade frágil (`11.222...` ≠ `11222...`).
- Validar nos serviços — espalharia a regra por cada ponto de escrita.
- Biblioteca externa de CNPJ — dependência extra sem ganho sobre ~20 linhas
  testadas (`app/core/validadores.py`).

## Consequências

- Unicidade independe do formato de entrada; CNPJ inválido responde `422`.
- Validação coberta por testes dedicados (`tests/test_schemas.py`).
