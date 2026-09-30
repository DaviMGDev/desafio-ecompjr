# API de Gerenciamento de Estoque

API em **FastAPI + PostgreSQL** para cadastro de fornecedores, categorias e produtos
e para auditoria de movimentações de estoque — desafio técnico da Trilha Back-End
Prosel 2026.2 (EcompJr/UEFS).

- Especificação: [`specs/SPEC.md`](specs/SPEC.md) — fonte da verdade do projeto
- Comportamentos BDD: [`specs/features/`](specs/features/)
- Decisões de arquitetura: [`docs/adr/`](docs/adr/)
- Documentação interativa: `http://localhost:8000/docs` (Swagger/OpenAPI)

## Sumário

- [Stack](#stack)
- [Como rodar](#como-rodar)
- [Configuração (.env)](#configuração-env)
- [Autenticação e perfis](#autenticação-e-perfis)
- [Endpoints](#endpoints)
- [Modelo de erro](#modelo-de-erro)
- [Regras de negócio](#regras-de-negócio)
- [Testes e CI](#testes-e-ci)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Decisões registradas (ADRs)](#decisões-registradas-adrs)

## Stack

- Python 3.12+ · FastAPI · Pydantic v2 · SQLAlchemy 2.x (sync, psycopg 3)
- PostgreSQL 16 (Docker Compose no desenvolvimento; serviço no CI)
- Alembic (migrations) · pytest + httpx (testes) · ruff (lint/format)
- uv como fluxo principal, com `requirements.txt` gerado para quem usa `pip`

## Como rodar

Pré-requisitos: Python 3.12+, [uv](https://docs.astral.sh/uv/) e Docker (Compose v2).

### Com uv (fluxo principal)

```bash
uv sync                                      # instala as dependências
cp .env.example .env                         # configure as variáveis
docker compose up -d db                      # sobe o PostgreSQL local
uv run alembic upgrade head                  # aplica as migrations
uv run python -m app.seed                    # cria o admin do .env
uv run uvicorn app.main:app --reload         # sobe a API em http://localhost:8000
```

### Com pip (alternativa sem uv)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d db
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

`requirements.txt` é um artefato gerado (`uv export --no-hashes`); não edite à mão.

### Comandos úteis

```bash
uv run pytest -q                             # testes (exigem o banco do compose)
uv run ruff check . && uv run ruff format .  # lint e formatação
uv run alembic revision --autogenerate -m "descrição da mudança"
uv run alembic upgrade head                  # aplica migrations
uv run alembic downgrade -1                  # reverte uma migration
```

## Configuração (.env)

| Variável             | Obrigatória | Descrição                                                        |
|----------------------|-------------|------------------------------------------------------------------|
| `DATABASE_URL`       | sim         | URL do SQLAlchemy com driver psycopg 3                           |
| `JWT_SECRET`         | sim         | Segredo da assinatura do JWT (use 32+ bytes e nunca commite)     |
| `JWT_EXPIRE_MINUTES` | não         | Validade do token em minutos (padrão 60)                         |
| `ADMIN_EMAIL`        | seed        | E-mail do admin criado por `python -m app.seed`                  |
| `ADMIN_PASSWORD`     | seed        | Senha do admin (armazenada apenas como hash argon2)              |

O `.env.example` traz valores de exemplo; o `.env` é ignorado pelo git.

## Autenticação e perfis

A API usa **JWT** (`Authorization: Bearer <token>`) com dois perfis:

- **leitor** — consulta todos os recursos (`GET`);
- **admin** — consulta e executa operações de escrita (`POST`/`PUT`/`DELETE`).

Rotas públicas: `GET /health` e `POST /auth/login`. As demais exigem token válido.

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@exemplo.com", "senha": "sua-senha"}'
# {"access_token": "eyJhbGciOiJIUzI1...", "token_type": "bearer"}

curl -s http://localhost:8000/produtos \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1..."
```

O admin é semeado pelo ambiente (`uv run python -m app.seed`) — não há rota pública
de cadastro de usuários. O token carrega o perfil no payload (`perfil`).

## Endpoints

Formato de cada rota: método, caminho, parâmetros, body de exemplo e respostas
previstas (JSON de exemplo). Erros comuns a várias rotas: `401` (sem token ou token
inválido), `403` (perfil leitor tentando escrever) e `500` (falha interna genérica).

### Infra

#### `GET /health` — público

Verifica se a API está no ar.

- 200: `{"status": "ok"}`

### Autenticação

#### `POST /auth/login` — público

Body:

```json
{ "email": "admin@exemplo.com", "senha": "sua-senha" }
```

- 200: `{"access_token": "eyJ...", "token_type": "bearer"}`
- 401: `{"detail": "E-mail ou senha inválidos"}`
- 422: `{"detail": [{"loc": ["body", "email"], "msg": "value is not a valid email address"}]}`

### Fornecedores

#### `POST /fornecedores` — admin

Body (o CNPJ pode vir com máscara; é armazenado sem máscara):

```json
{
  "nome": "Distribuidora Aurora",
  "cnpj": "11.222.333/0001-81",
  "telefone": "75 99999-0000",
  "email": "contato@aurora.com"
}
```

- 201: `{"id": 1, "nome": "Distribuidora Aurora", "cnpj": "11222333000181", "telefone": "75 99999-0000", "email": "contato@aurora.com"}`
- 409: `{"detail": "CNPJ já cadastrado"}` · `{"detail": "E-mail já cadastrado"}`
- 422: `{"detail": [{"loc": ["body", "cnpj"], "msg": "Value error, CNPJ inválido"}]}`

#### `GET /fornecedores` — leitor

Query: `limit` (1–100, padrão 20), `offset` (padrão 0), `nome` (trecho, sem
diferenciar caixa).

- 200: `[{"id": 1, "nome": "Distribuidora Aurora", "cnpj": "11222333000181", "telefone": "75 99999-0000", "email": "contato@aurora.com"}]`

#### `GET /fornecedores/{id}` — leitor

- 200: fornecedor (mesmo formato acima)
- 404: `{"detail": "Fornecedor não encontrado"}`

#### `PUT /fornecedores/{id}` — admin

Body: os mesmos campos do `POST` (representação completa).

- 200: fornecedor atualizado
- 404: `{"detail": "Fornecedor não encontrado"}`
- 409: `{"detail": "CNPJ já cadastrado"}` · `{"detail": "E-mail já cadastrado"}`

#### `DELETE /fornecedores/{id}` — admin

- 204: sem corpo
- 404: `{"detail": "Fornecedor não encontrado"}`
- 409: `{"detail": "Fornecedor possui produtos vinculados"}`

### Categorias

#### `POST /categorias` — admin

Body: `{"nome": "Bebidas"}`

- 201: `{"id": 1, "nome": "Bebidas"}`
- 409: `{"detail": "Categoria já cadastrada"}` (nome único sem diferenciar caixa)

#### `GET /categorias` — leitor

Query: `limit` (1–100, padrão 20), `offset` (padrão 0).

- 200: `[{"id": 1, "nome": "Bebidas"}]`

#### `GET /categorias/{id}` — leitor

- 200: `{"id": 1, "nome": "Bebidas"}`
- 404: `{"detail": "Categoria não encontrada"}`

#### `PUT /categorias/{id}` — admin

Body: `{"nome": "Bebidas e Sucos"}` · 200: categoria atualizada · 404 · 409.

#### `DELETE /categorias/{id}` — admin

- 204: sem corpo
- 409: `{"detail": "Categoria possui produtos vinculados"}` (§ 2.c do enunciado)

### Produtos

#### `POST /produtos` — admin

Body (o saldo **não** é aceito no payload — só muda por movimentação):

```json
{
  "nome": "Chá preto 500g",
  "sku": "CHA-500",
  "preco_custo": "8.50",
  "preco_venda": "14.90",
  "quantidade_minima": 5,
  "categoria_id": 1,
  "fornecedor_id": 1
}
```

- 201: `{"id": 1, "nome": "Chá preto 500g", "sku": "CHA-500", "preco_custo": "8.50", "preco_venda": "14.90", "quantidade_minima": 5, "categoria_id": 1, "fornecedor_id": 1, "quantidade_em_estoque": 0, "data_cadastro": "2026-09-30T12:00:00Z"}`
- 404: `{"detail": "Categoria não encontrada"}` · `{"detail": "Fornecedor não encontrado"}`
- 409: `{"detail": "SKU já cadastrado"}`
- 422: `{"detail": [{"loc": ["body", "quantidade_em_estoque"], "msg": "Extra inputs are not permitted"}]}`

#### `GET /produtos` — leitor

Query: `limit`, `offset`, `nome`, `categoria_id`, `fornecedor_id`.

- 200: lista de produtos (formato acima)

#### `GET /produtos/estoque-baixo` — leitor

Produtos com `quantidade_em_estoque <= quantidade_minima`, do mais crítico ao
menos crítico (§ 2.d). Query: `limit`, `offset`.

- 200: `[{"id": 1, ..., "quantidade_em_estoque": 3, "quantidade_minima": 5}]`
- 200 (vazio): `[]`

#### `GET /produtos/{id}` — leitor

- 200: produto · 404: `{"detail": "Produto não encontrado"}`

#### `PUT /produtos/{id}` — admin

Body: os mesmos campos do `POST`. Enviar `quantidade_em_estoque` → 422.

- 200: produto atualizado · 404 · 409 (SKU)

#### `DELETE /produtos/{id}` — admin

- 204: sem corpo
- 409: `{"detail": "Produto possui movimentações registradas"}`

### Movimentações de estoque (imutáveis)

Somente `POST` e `GET`; não existem rotas de edição/exclusão.

#### `POST /movimentacoes` — admin

Body (a `data` é definida pelo servidor):

```json
{
  "produto_id": 1,
  "tipo": "entrada",
  "quantidade": 10,
  "fornecedor_id": 1,
  "observacao": "Reposição de setembro"
}
```

`tipo` aceita `entrada` ou `saida`; `quantidade` é sempre positiva (o sinal vem do
tipo). Entrada soma ao saldo; saída subtrai — na **mesma transação** (ADR-0003).

- 201: `{"id": 1, "produto_id": 1, "fornecedor_id": 1, "tipo": "entrada", "quantidade": 10, "data": "2026-09-30T12:00:00Z", "observacao": "Reposição de setembro"}`
- 404: `{"detail": "Produto não encontrado"}` · `{"detail": "Fornecedor não encontrado"}`
- 409: `{"detail": "Saldo insuficiente para a saída"}`
- 422: `{"detail": [{"loc": ["body", "quantidade"], "msg": "Input should be greater than 0"}]}`

#### `GET /movimentacoes` — leitor

Query (todas opcionais): `produto_id`, `tipo`, `fornecedor_id`, `data_inicio`,
`data_fim` (ISO 8601 com offset, **inclusivos** nas duas pontas), `limit`, `offset`.

- 200: `[{"id": 1, "produto_id": 1, "fornecedor_id": 1, "tipo": "entrada", "quantidade": 10, "data": "2026-09-30T12:00:00Z", "observacao": null}]`
- 422: `{"detail": "data_inicio não pode ser maior que data_fim"}`

#### `GET /movimentacoes/{id}` — leitor

- 200: movimentação · 404: `{"detail": "Movimentação não encontrada"}`

#### `PUT` / `PATCH` / `DELETE /movimentacoes/{id}`

- 405: `{"detail": "Method Not Allowed"}` — a imutabilidade é garantida pela API e
  coberta por testes.

## Modelo de erro

Envelope único `{"detail": ...}`: string nos erros de negócio, lista de erros no
`422` de validação. Nenhuma resposta de falha devolve `200` nem stack trace.

| Situação                                   | Status | Exemplo de `detail`                          |
|--------------------------------------------|--------|----------------------------------------------|
| Validação de schema                        | 422    | lista com `loc` e `msg` por campo            |
| Recurso (ou referência no body) inexistente| 404    | `"Produto não encontrado"`                    |
| Unicidade / vínculo de exclusão / saldo    | 409    | `"Saldo insuficiente para a saída"`           |
| Sem token / token inválido                 | 401    | `"Token de autenticação ausente"`             |
| Perfil sem permissão de escrita            | 403    | `"Perfil sem permissão de escrita"`           |
| Método não permitido (movimentações)       | 405    | `"Method Not Allowed"`                        |
| Falha interna                              | 500    | `"Erro interno do servidor"` (log no servidor)|

## Regras de negócio

- **Movimentação é imutável**: apenas criação e leitura; `PUT`/`PATCH`/`DELETE`
  respondem `405`.
- **Atomicidade do saldo**: a movimentação e a atualização de saldo acontecem na
  mesma transação, com `SELECT ... FOR UPDATE` na linha do produto (lock
  pessimista) e `CHECK (quantidade_em_estoque >= 0)` no banco como backstop.
  Duas saídas simultâneas nunca estouram o estoque (teste de concorrência).
- **Saldo somente leitura**: `quantidade_em_estoque` não é aceita em payloads de
  produto (`422`); muda apenas por movimentação.
- **Exclusões com vínculo** (`RESTRICT` + `409`): categoria com produtos,
  fornecedor com produtos e produto com movimentações.
- **Unicidades no banco**: `produto.sku`, `fornecedor.cnpj`, `fornecedor.email` e
  `categoria.nome`; e-mail e nome de categoria são únicos sem diferenciar caixa.
- **Consultas avançadas**: `/produtos/estoque-baixo` (`saldo <= mínimo`) e
  filtros de movimentação por período (inclusivo), fornecedor, tipo e produto.
- **Paginação**: `limit` (máx. 100) e `offset` com padrão 20.

## Testes e CI

```bash
uv run pytest -q
```

A suíte cobre as regras de negócio além do caminho feliz: imutabilidade, exclusão
com vínculo, unicidades, saldo após entrada/saída, consultas e **concorrência**
(duas saídas simultâneas com threads e conexões reais). As fixtures de API usam
transação revertida por teste, sem depender de ordem (`pytest-randomly`).

O workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) roda em cada
push: lint (`ruff`), migration (`alembic upgrade head`) e testes, com um serviço
PostgreSQL 16.

## Estrutura do projeto

```
app/
  main.py            # aplicação FastAPI (handlers + routers)
  db.py              # engine e sessão (dependency injection)
  seed.py            # criação do admin a partir do ambiente
  core/              # config, segurança (hash/JWT), validadores, integridade
  models/            # SQLAlchemy: fornecedor, categoria, produto, movimentação, usuário
  schemas/           # Pydantic: entrada/saída da API
  routers/           # rotas por recurso
  services/          # regras de negócio e transações
migrations/          # Alembic
specs/               # SPEC.md, index, log e features BDD
docs/adr/            # decisões de arquitetura
tests/               # pytest (fixtures isoladas por transação)
```

## Decisões registradas (ADRs)

| #    | Decisão |
|------|---------|
| [0001](docs/adr/0001-estoque-minimo-por-produto.md) | Estoque mínimo por produto (`quantidade_minima`, default 0) |
| [0002](docs/adr/0002-fornecedor-na-movimentacao.md) | Fornecedor gravado na movimentação (filtro com histórico estável) |
| [0003](docs/adr/0003-lock-pessimista-no-saldo.md) | Lock pessimista + CHECK para o saldo (concorrência) |
| [0004](docs/adr/0004-envelope-de-erro.md) | Envelope de erro `{"detail": ...}` com handlers globais |
| [0005](docs/adr/0005-exclusoes-com-restrict.md) | Exclusões com `RESTRICT` + 409 |
| [0006](docs/adr/0006-superficie-da-api.md) | Rotas pt-BR, PUT único, saldo somente leitura |
| [0007](docs/adr/0007-filtros-e-paginacao.md) | Período inclusivo e paginação `limit`/`offset` |
| [0008](docs/adr/0008-ordem-dos-diferenciais.md) | Ordem dos diferenciais (auth, testes/CI, concorrência) |
| [0009](docs/adr/0009-layout-e-stack.md) | Layout em camadas, SQLAlchemy sync, Pydantic v2 |
