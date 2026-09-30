# ADR-0010: Unicidade sem diferenciar caixa com índice funcional

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O enunciado (§ 2.b) exige e-mail de fornecedor e nome de categoria únicos.
Normalizar (`strip`/minúsculas) apenas na aplicação não protege contra escritas
diretas no banco (migrations, scripts, psql) nem contra corridas entre requisições.

## Decisão

Dupla proteção:

1. normalização na borda (schemas Pydantic/`str_strip_whitespace` + minúsculas);
2. índice único funcional `lower(coluna)` no banco (`uq_fornecedores_email_lower`,
   `uq_categorias_nome_lower`), como backstop independente da aplicação.

## Alternativas consideradas

- Somente normalização na aplicação — duplicatas entrariam por qualquer escrita
  que não passe pela API.
- Extensão `citext` do PostgreSQL — resolveria, mas adiciona uma dependência de
  extensão sem ganho sobre o índice funcional.

## Consequências

- Unicidade robusta mesmo fora da API; a violação vira `409` com mensagem clara
  (mapeada pelo nome da constraint no handler de integridade).
- Índices funcionais (não `UNIQUE CONSTRAINT` nomeada), ambos já presentes nas
  migrations de schema.
