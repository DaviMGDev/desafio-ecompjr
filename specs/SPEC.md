---
type: spec
title: "API de Gerenciamento de Estoque — Specification"
description: "API FastAPI + PostgreSQL para fornecedores, categorias, produtos e auditoria de movimentações de estoque (Prosel 2026.2)"
tags: [spec]
sections: [context, users, user-stories, architecture, data-model, api, nfr, stack, ops, decisions]
created: "2026-09-30"
updated: "2026-09-30"
---

# API de Gerenciamento de Estoque — Specification

*Esta especificação declara o próprio contrato: toda seção `##` abaixo aparece em
`sections:` no frontmatter, e nada aparece sem declaração.*

## Context

A loja de variedades "愚公移山 Variedades" controla o estoque no papel: não há
relação entre produto, fornecedor e categoria, e o histórico de entradas/saídas
não é auditável. O objetivo é concentrar esses dados numa API que sirva de base
para futuras aplicações web e mobile.

Fonte normativa: `desafio-tecnico-backend-prosel-2026.2/desafio-tecnico-backend-prosel-2026.2.md`.
Em caso de conflito, o enunciado vence este documento. Itens sem respaldo direto
no enunciado estão marcados como **decisão de projeto** (aceita na proposta v1 de 2026-09-30).
Comportamentos acordados vivem em `specs/features/*.feature` (Gherkin pt-BR).

Escopo: CRUD de fornecedores, categorias e produtos; movimentações de estoque
imutáveis com atualização transacional do saldo; consultas avançadas de estoque
mínimo e filtros de movimentação; erros padronizados; OpenAPI + README. Fora de
escopo do enunciado: front-end e multiusuário complexo (§ 3.a cobre apenas JWT +
perfis como diferencial). O front-end foi construído depois como extra (D10–D12):
consome a API como cliente externo e não altera este serviço.

Barema (§ 6): CRUD 1, consultas 1, erros 1, documentação 1, commits 2, qualidade
2, diferenciais até 2.

## Users

- **Gestor(a) da loja** — administra catálogo, fornecedores, categorias e
  movimentações; decide o que entra e sai.
- **Funcionário(a)/vendedor(a)** — consulta produtos e registra movimentações;
  no diferencial de auth tem perfil de leitura.
- **Aplicações consumidoras** — apps web/mobile futuros; consomem JSON, o
  contrato OpenAPI e o modelo de erro padronizado.

## User Stories

Story: US-001 — Cadastro de fornecedores

Como gestor(a), quero manter fornecedores, para saber quem fornece cada produto.

Critérios de aceitação (EARS):

- O sistema DEVE rejeitar fornecedor com `cnpj` já cadastrado com HTTP 409 e mensagem explicativa.
- O sistema DEVE rejeitar fornecedor com `email` já cadastrado com HTTP 409.
- Quando um fornecedor ainda tiver produtos vinculados, o sistema DEVE rejeitar a exclusão com HTTP 409 e manter o registro.

Story: US-002 — Catálogo de categorias

Como gestor(a), quero manter categorias únicas, para classificar os produtos.

- Quando um nome de categoria já existir (ignorando caixa), o sistema DEVE responder HTTP 409.
- Quando uma categoria tiver produtos vinculados, o sistema DEVE rejeitar a exclusão com HTTP 409 (§ 2.c).

Story: US-003 — Cadastro de produtos

Como gestor(a), quero manter produtos com preços, categoria e fornecedor.

- O sistema DEVE garantir `sku` único no banco (HTTP 409 em duplicidade).
- Enquanto o saldo só puder mudar por movimentação, o sistema DEVE recusar payloads de produto que tentem definir `quantidade_em_estoque` (HTTP 422).
- Quando `categoria_id` ou `fornecedor_id` não existir, o sistema DEVE responder HTTP 404 com mensagem explicativa.

Story: US-004 — Movimentação de estoque

Como funcionário(a), quero registrar entradas e saídas, para manter o saldo confiável.

- Quando uma entrada for registrada, o sistema DEVE somar a quantidade ao saldo do produto na mesma transação.
- Se uma saída exceder o saldo, então o sistema DEVE responder HTTP 409 e nenhuma alteração DEVE persistir.
- O sistema DEVE responder 405 para PUT/PATCH/DELETE em `/movimentacoes*` (imutabilidade).
- O sistema DEVE registrar `data` no servidor, não no cliente.

Story: US-005 — Consultas avançadas

Como gestor(a), quero ver produtos em/abaixo do estoque mínimo e filtrar movimentações.

- O sistema DEVE retornar produtos com `quantidade_em_estoque <= quantidade_minima` em `GET /produtos/estoque-baixo`.
- O sistema DEVE permitir filtrar `/movimentacoes` por `data_inicio` e `data_fim` (inclusivos, ISO 8601) e por `fornecedor_id`.

Story: US-006 — Segurança (diferencial § 3.a)

Como administrador(a), quero proteger a API por perfil, para separar leitura e escrita.

- Quando a requisição não trouxer token válido, o sistema DEVE responder 401 em rotas protegidas.
- Onde o perfil for de leitura, o sistema DEVE responder 403 para operações de escrita.

## Architecture

Componentes: FastAPI (rotas + validação Pydantic v2) → camada de serviços
(regras de negócio e transações) → SQLAlchemy 2.x (sync, psycopg 3) → PostgreSQL.
Sem `repositories` dedicados nesta escala: os serviços usam a `Session` diretamente,
reduzindo cerimônia sem tirar testabilidade (decisão de projeto).

Fluxo crítico — criar movimentação:

1. Abre a transação (dependency de sessão, commit/rollback explícitos).
2. `SELECT ... FOR UPDATE` na linha do produto (lock pessimista; ver Decisions).
3. Valida saldo para saída; insuficiência → 409 e rollback total.
4. Insere a movimentação e atualiza `quantidade_em_estoque` (±quantidade).
5. Commit único; `CHECK` de banco como backstop.

Fluxo de exclusão: pré-checagem de vínculos na aplicação → 409 com mensagem;
FKs `RESTRICT` no banco impedem a corrida residual.

Autenticação (diferencial aceito): JWT (PyJWT) com `sub` e `perfil`;
usuário semeado por variável de ambiente/migration; sem rota pública de cadastro.

## Data Model

Identificadores em ASCII sem acentos (`preco_custo`, `preco_venda`); valores e
mensagens em pt-BR. Unicidades garantidas no banco (§ 2.b): `produto.sku`,
`fornecedor.cnpj`, `fornecedor.email`, `categoria.nome`.

### Fornecedor

| campo    | tipo      | regra                                                            |
|----------|-----------|------------------------------------------------------------------|
| id       | PK        |                                                                  |
| nome     | text      | obrigatório                                                      |
| cnpj     | char(14)  | único; armazenado sem máscara; dígitos verificadores validados   |
| telefone | text      | obrigatório (§ 2.b)                                              |
| email    | text      | único, normalizado em minúsculas                                 |

### Categoria

| campo | tipo | regra                                                       |
|-------|------|-------------------------------------------------------------|
| id    | PK   |                                                             |
| nome  | text | único (índice funcional em `lower(nome)`), sem espaços nas pontas |

### Produto

| campo                   | tipo          | regra                                                              |
|-------------------------|---------------|--------------------------------------------------------------------|
| id                      | PK            |                                                                    |
| nome                    | text          | obrigatório                                                        |
| sku                     | text          | único                                                              |
| preco_custo / preco_venda | numeric(12,2) | `>= 0`; `Decimal` (nunca float)                                  |
| quantidade_em_estoque   | integer       | `>= 0` (CHECK); somente leitura na API                             |
| quantidade_minima       | integer       | `>= 0`, default 0 — **decisão de projeto** (§ 2.d não define campo) |
| data_cadastro           | timestamptz   | default `now()`, UTC                                               |
| categoria_id            | FK → categorias | `ON DELETE RESTRICT`, obrigatório                                |
| fornecedor_id           | FK → fornecedores | `ON DELETE RESTRICT`, obrigatório                              |

### Movimentacao

| campo         | tipo              | regra                                                                             |
|---------------|-------------------|-----------------------------------------------------------------------------------|
| id            | PK                |                                                                                   |
| produto_id    | FK → produtos     | `ON DELETE RESTRICT`, obrigatório                                                 |
| fornecedor_id | FK → fornecedores | nullable, `ON DELETE RESTRICT`; registrado na criação — **decisão de projeto** (§2.d) |
| tipo          | enum              | `entrada` \| `saida`                                                              |
| quantidade    | integer           | `> 0` (CHECK)                                                                     |
| data          | timestamptz       | default `now()`, definida pelo servidor                                           |
| observacao    | text              | opcional, livre                                                                   |

Imutabilidade: sem rotas de escrita além do POST; nenhum efeito colateral altera
movimentações; testes garantem 405 para PUT/PATCH/DELETE.

## API

Estilo: recursos em pt-BR, JSON em pt-BR, paginação `limit`/`offset` (default 20,
máx 100), ordenação documentada. Exemplos completos no OpenAPI (docstrings +
`responses=`) e espelhados no README (§ 2.g).

| método          | rota                     | descrição                                              | sucesso |
|-----------------|--------------------------|--------------------------------------------------------|---------|
| POST            | /fornecedores            | cria fornecedor                                        | 201     |
| GET             | /fornecedores            | lista (paginação, filtro `nome`)                       | 200     |
| GET             | /fornecedores/{id}       | detalhe                                                | 200     |
| PUT             | /fornecedores/{id}       | atualiza                                               | 200     |
| DELETE          | /fornecedores/{id}       | exclui sem vínculo                                     | 204     |
| POST/GET/PUT/DELETE | /categorias[...]      | idem, com nome único                                   | 201/200/204 |
| POST/GET/PUT/DELETE | /produtos[...]        | idem, saldo somente leitura                            | 201/200/204 |
| GET             | /produtos/estoque-baixo  | `saldo <= quantidade_minima`, ordenado por criticidade | 200     |
| POST            | /movimentacoes           | cria entrada/saída (atômico)                           | 201     |
| GET             | /movimentacoes           | filtros `produto_id`, `tipo`, `fornecedor_id`, `data_inicio`, `data_fim` | 200 |
| GET             | /movimentacoes/{id}      | detalhe (somente leitura)                              | 200     |
| GET             | /health                  | smoke test do CI                                       | 200     |

Erros: envelope único `{"detail": ...}` — string nas falhas de negócio, lista de
mensagens no 422 de validação. Mapa: 422 schema; 404 recurso ausente (inclusive
FK referenciada no body); 409 unicidade, vínculo de exclusão, saldo insuficiente;
400 requisição semanticamente inválida fora do schema; 500 interno sem stack
trace; 401/403 com auth (diferencial). Mensagens em pt-BR; nunca 200 em falha (§ 2.e).

## NFR

- Concorrência (§ 3.c): lock pessimista por produto + transação única + CHECK;
  teste com requisições simultâneas garante que só uma saída vence o período.
- Segurança (§ 3.a, diferencial aceito): hash de senha (argon2/bcrypt), JWT assinado
  por segredo em variável de ambiente, perfis leitor/admin; nada de segredo no repo.
- Erros: nenhum detalhe interno vaza; todo 500 é genérico com log no servidor.
- Persistência: `Decimal` para dinheiro; `timestamptz` em UTC.
- Qualidade: ruff + pytest no CI a cada push (§ 3.b); foco nas regras de negócio,
  não só no caminho feliz.

Critérios EARS:

- O sistema DEVE responder a toda falha com o envelope padronizado e sem stack trace.
- Quando duas saídas concorrentes disputarem o mesmo produto, o sistema DEVE aplicar exatamente uma delas e manter o saldo final correto.

## Stack

- Python 3.12+, uv (fluxo principal) + `requirements.txt` gerado (`uv export`).
- FastAPI, Pydantic v2, SQLAlchemy 2.x (sync, psycopg 3), Alembic, PostgreSQL 16.
- Testes: pytest + httpx; CI GitHub Actions com serviço PostgreSQL.
- Qualidade: ruff (lint + format). Docker Compose para o banco local.

## Ops

- `.env.example` com `DATABASE_URL` (e `JWT_SECRET` se auth); `.env` fora do git.
- `docker compose up -d db` para o PostgreSQL local; migrations desde o primeiro
  commit (`alembic upgrade head`).
- README: subir API (`uv run uvicorn app.main:app --reload`), testes, lint; para
  cada rota, método, path, params, body de exemplo e respostas 2xx/4xx com JSON.
- Collection Postman/Insomnia opcional e complementar.

## Decisions

Decisões aceitas na proposta v1 (2026-09-30); cada uma vira ADR em `docs/adr/`
conforme for implementada (fluxo do AGENTS.md):

| #  | decisão                                                                 | trade-off registrado                                                  |
|----|-------------------------------------------------------------------------|------------------------------------------------------------------------|
| D1 | `quantidade_minima` no produto, default 0                               | campo extra fora de §2.b vs consulta intrínseca por produto            |
| D2 | `fornecedor_id` gravado na movimentação (nullable)                      | histórico estável vs coluna extra; join pelo produto reescreveria o passado |
| D3 | lock pessimista (`SELECT ... FOR UPDATE`) + CHECK de saldo              | contenção de escrita vs simplicidade/retries                           |
| D4 | envelope `{"detail": ...}` + handlers globais                           | zero custom vs códigos de erro para máquina                            |
| D5 | FKs `RESTRICT` + 409 com mensagem                                       | recursos indeletáveis com vínculo vs auditoria íntegra                 |
| D6 | rotas pt-BR; PUT como única edição; saldo read-only                     | aderência ao enunciado vs padrão internacional                         |
| D7 | período `datetime` ISO 8601 inclusivo; paginação limit/offset           | precisão de fuso vs usabilidade de date-only                           |
| D8 | diferenciais: concorrência → testes/CI → auth (auth corta primeiro)     | pontos extras vs risco de prazo                                        |
| D9 | camadas enxuto, SQLAlchemy sync, Pydantic v2                            | clareza/defesa vs DDD/async                                            |
| D10 | front-end FastHTML em serviço ASGI separado consumindo a API; JWT em sessão assinada | backend intocado e contrato exercitado vs. um processo extra (ADR-0014) |
| D11 | dependências do front-end em grupo opcional `frontend` no pyproject raiz | um lockfile/um ambiente vs. job de CI com `--group frontend` (ADR-0015) |
| D12 | seed do leitor por `LEITOR_EMAIL`/`LEITOR_PASSWORD` para a demo do 403 | demo ao vivo vs. pequeno diff no seed/serviço, com ADR (0016)           |
