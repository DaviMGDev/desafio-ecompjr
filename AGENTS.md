# desafio-ecompjr — API de Gerenciamento de Estoque

> Desafio técnico da Trilha Back-End Prosel 2026.2 (EcompJr/UEFS): uma API em
> **FastAPI + PostgreSQL** para cadastro de fornecedores, produtos e categorias e
> para auditoria de movimentações de estoque.
>
> **Status atual: API concluída; painel web (extra) implementado.** A API está
> bootstrapped (`pyproject.toml`, `app/` em 6 camadas, 2 migrations Alembic, 16 ADRs
> aceitos, 79 testes, CI verde, README detalhado). O painel FastHTML vive em
> `frontend/` e consome a API por HTTP (ADR-0014) — o backend é intocável por ele.
> O trabalho restante é **preparação para a defesa técnica (§ 6)** — material local
> em `.pi/defesa/`. Não faça bootstrap nem re-scaffold: o código existente é o
> contrato.

## Fonte da verdade

| Caminho | Papel |
|---|---|
| `desafio-tecnico-backend-prosel-2026.2/desafio-tecnico-backend-prosel-2026.2.md` | Enunciado oficial (**read-only** — nunca editar) |
| `specs/SPEC.md` | Contrato spec-md: contexto, histórias, arquitetura, dados, API, decisões |
| `specs/index.md` + `specs/log.md` | Registro do nó MKF e log de atividades — atualize o log ao mexer na spec |
| `specs/features/` | Comportamentos acordados em Gherkin pt-BR (59 cenários) |
| `docs/adr/` | ADRs 0001–0016 aceitos e implementados (ver *Registro de decisões (ADR)*) |
| `README.md` | Documentação de entrega (setup, rotas, exemplos) — espelha o OpenAPI |
| `.pi/` | Estado local do agente (planos, defesa) — gitignored, nunca é entrega |

Em caso de conflito entre um `specs/*` e o enunciado, o **enunciado vence**.
Não invente requisitos: se algo não está no enunciado, marque como decisão de projeto.

## Fase atual

Implementação encerrada (API + painel); o próximo trabalho é a **defesa técnica
(§ 6)**: estudar o fluxo de movimentação, o lock pessimista, as decisões dos ADRs
e treinar em voz alta (registro em `.pi/defesa/`). Não adicione funcionalidade
fora do enunciado sem pedido explícito.

## Idioma e escrita

- **Artefatos não-código em pt-BR:** README, docs, `specs/`, ADRs, issues, PRs,
  mensagens de commit, comentários e docstrings.
- **Código não é artefato textual:** identificadores, nomes de arquivos, rotas,
  nomes de tabelas/colunas e chaves JSON são decisões de estilo — mantenha
  consistência e registre a escolha em `specs/` antes de espalhar um padrão novo.
- **Não traduza expressões consagradas em inglês**, mesmo em texto pt-BR:
  *web scraping, race condition, commit, deploy, container, fixture, migration,
  endpoint, payload, lock otimista/pessimista* ficam como estão.
- **Conversa com o usuário** pode ser no idioma que ele usar; código e artefatos
  continuam seguindo as regras acima.

## Stack e decisões

Definido pelo enunciado (não é negociável):

- **Python** + **FastAPI** para a API
- **PostgreSQL** para persistência
- **SQLAlchemy** (ORM) e **Alembic** (migrations) — recomendação explícita da seção 7.4
- Documentação via **OpenAPI/Swagger** gerada pelo FastAPI + README detalhado (§ 2.g)

Decidido pelo candidato:

- Gerenciamento de ambiente com **uv** como fluxo principal, mantendo
  **compatibilidade com `pip` + `requirements.txt`** (quem avalia pode não ter `uv`)
- Estrutura decidida (ADR-0009): `app/routers` (HTTP + OpenAPI) → `app/services`
  (regras de negócio e transações, usando `Session` direto, sem repositórios) →
  `app/models` (SQLAlchemy) com `app/schemas` (Pydantic) separados; `app/core`
  (config, segurança, validadores, integridade) e `app/api` (deps, handlers de
  erro, helpers de OpenAPI). Módulos novos seguem essa divisão.

Toda decisão relevante (transações, locks, estratégia de erro, modelagem de
relacionamentos) deve ser explicável em voz alta — haverá **defesa técnica** (§ 6).

## Comandos

Fluxo principal (`uv`):

```bash
docker compose up -d db                    # sobe o PostgreSQL local
uv sync                                   # instala deps do pyproject + lock
uv run uvicorn app.main:app --reload      # sobe a API em dev
uv run alembic revision --autogenerate -m "cria tabela produtos"
uv run alembic upgrade head               # aplica migrations
uv run python -m app.seed                 # cria admin (e leitor, se LEITOR_*) do .env
uv run pytest -q                          # testes (banco <DATABASE_URL>_test próprio)
uv run ruff check . && uv run ruff format .

# painel web (extra — ADR-0014/0015): API em :8000 e painel em :5001
uv sync --group frontend
uv run --group frontend python -m frontend.main
uv run --group frontend pytest frontend/tests
```

Compatibilidade com `pip` (para quem for avaliar sem `uv`):

```bash
uv export --no-hashes -o requirements.txt   # regenerar SEMPRE que mexer em deps
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

- `requirements.txt` é **artefato gerado** — nunca edite à mão; se o fluxo mudar,
  ele é regenerado pelo `uv export`.
- Banco local: `docker compose up -d db` sobe o PostgreSQL 16 (config em `docker-compose.yml`).
- Testes usam um banco próprio (`<DATABASE_URL>_test`, criado na primeira execução;
  ou `TEST_DATABASE_URL`): dados de demo no banco principal não afetam a suíte.
- Nunca commite `.env`, `venv/`, `__pycache__/`, dumps de banco ou credenciais.

## Invariantes de domínio

Resumo operacional — os detalhes ficam em `specs/` quando existir. Nunca viole:

1. **Movimentação de estoque é imutável**: só `POST` e leitura. Não crie rota de
   `PUT`/`PATCH`/`DELETE` para movimentações, nem permita alterá-las por efeito colateral.
2. **Toda movimentação atualiza o saldo do produto na mesma transação** que a insere;
   saída maior que o saldo → 409 com rollback total. Lock pessimista
   (`SELECT ... FOR UPDATE` na linha do produto) serializa a seção crítica (ADR-0003).
3. **Categoria com produtos vinculados não pode ser excluída** (§ 2.c) — responda com erro claro, não com 500.
4. **Unicidade garantida no banco**, não apenas na aplicação: `produto.sku`,
   `fornecedor.cnpj`, `fornecedor.email`, `categoria.nome`.
5. **Integridade referencial** explícita: FKs com `ON DELETE RESTRICT` em todas as
   relações (ADR-0005); exclusão com vínculo → 409, nunca 500.
6. **Consulta avançada é requisito obrigatório**: produtos em/abaixo do estoque mínimo
   e filtro de movimentações por período e/ou fornecedor.
7. **Erros padronizados**: envelope único `{"detail": ...}` (ADR-0004), HTTP correto
   (400/404/409/422 conforme o caso, 500 para falhas internas), **sem stack trace** e
   **sem 200 em requisição falha**.

## Erros, validação e documentação da API

- Decidido (ADR-0004): envelope único `{"detail": ...}` — string nas falhas de
  negócio, lista no 422 do Pydantic. Handlers globais em `app/api/errors.py`
  (`IntegrityError` → 409; exceção não tratada → 500 logado, sem stack trace).
- Services levantam `HTTPException` direto com mensagem pt-BR; o router não repete
  validação que o schema cobre. Colisão de unicidade se mapeia com
  `conflito_de_integridade` (`app/core/integridade.py`) + `_MENSAGENS_DE_CONFLITO`.
- Cada endpoint: `responses=` com exemplos 2xx/4xx via helpers de
  `app/api/openapi.py` (`resposta`, `RESPOSTAS_LEITURA`, `RESPOSTAS_ESCRITA`)
  e espelho no `README.md`. Collection Postman/Insomnia é opcional e complementar.

## Autenticação e perfis (diferencial § 3.a aceito)

- `main.py` protege todos os routers com `dependencies=[Depends(usuario_atual)]`;
  público apenas `/health` e `POST /auth/login`. **Router novo precisa da dependência.**
- Escrita: `dependencies=[Depends(exigir_admin)]` na própria rota; leitura: qualquer
  perfil autenticado. 401 = token ausente/inválido; 403 = leitor tentando escrever.
- Segredos só via `.env` (`JWT_SECRET`, `JWT_EXPIRE_MINUTES`); admin semeado por
  `uv run python -m app.seed` (`ADMIN_EMAIL`/`ADMIN_PASSWORD`). Nunca commite segredo.

## Qualidade de código e comentários

- Código explica **o que** faz; comentários explicam **por que** (§ 2.g).
- Comente apenas: decisão arquitetural, regra de negócio não óbvia, transação/lock,
  contorno de limitação conhecida. Comentário que repete a linha é ruído.
- Justificativas de transação (ex.: "inserir movimentação e atualizar saldo precisam
  ser atômicos") devem estar no código e no `specs/`.
- Type hints em funções públicas; schemas Pydantic separados de models SQLAlchemy;
  sessão de banco via dependency injection, com commit/rollback explícitos.
- Prefira nomes de domínio claros a abreviações; evite `utils.py` genérico.

## Git e commits

Vale nota (§ 2.f e barema: **2 pontos**) — trate como requisito, não como formalidade.

- **Conventional Commits obrigatórios**: `feat:`, `fix:`, `docs:`, `refactor:`,
  `test:`, `chore:`, `build:`, `perf:`. Prefixo em inglês, descrição em pt-BR
  (`feat: adiciona endpoint de movimentação de estoque`).
- Escopo opcional e útil: `fix(produtos): ...`, `test(movimentacoes): ...`.
- **Commits atômicos e incrementais ao longo das 4 semanas.** Não acumule um
  "commit final" gigante; não faça commit de código que não roda.
- Um commit = uma intenção; não misture refactor de formatação com mudança de regra.
- Nunca `git commit --amend`/`push --force` em histórico já compartilhado sem pedir.

## Testes e CI (diferencial)

- Cada teste roda numa transação externa revertida no fim via savepoint (ADR-0012).
  Não crie fixture que commita no banco real nem dependa de ordem de execução
  (`pytest-randomly` roda fora de ordem de propósito).
- `client` já autentica como admin; `client_sem_auth` e `cliente_leitor` cobrem
  401/403. Teste novo entra no `tests/test_<recurso>.py` correspondente.
- Cubra as regras de negócio, não só o caminho feliz: imutabilidade da movimentação,
  exclusão de categoria com produtos, unicidade de `cnpj`/`email`/`sku`, saldo após entrada/saída.
- CI (`.github/workflows/ci.yml`): Postgres 16 como service, `uv sync --locked`, ruff,
  `alembic upgrade head` e pytest. Mexeu em dependência → rode
  `uv export --no-hashes -o requirements.txt` e garanta `uv.lock` atualizado
  (o `--locked` quebra a run se não).

## Segurança e concorrência (diferenciais)

- § 3.a: JWT + autorização por perfil (leitura vs. administração). Nunca commite segredo;
  use variáveis de ambiente.
- § 3.c: evite saldo incorreto com requisições concorrentes — transações bem modeladas
  e lock otimista ou pessimista. Escolha, implemente e **documente o trade-off**
  (`SELECT ... FOR UPDATE` vs. coluna de versão).

## Uso de IA e defesa técnica

A § 6 penaliza código que o candidato não consegue explicar — isso muda o
comportamento esperado do agente:

- **Explique antes de gerar.** Ao implementar algo não trivial, diga o porquê
  (transação, lock, política de delete) e as alternativas descartadas.
- **Não produza código inauditável.** Se um trecho não pode ser reescrito de memória
  pelo usuário, ele não deve entrar no repositório sem revisão e explicação.
- **Registre decisões** em `docs/adr/` à medida que forem tomadas, para a defesa — fluxo completo na seção *Registro de decisões (ADR)*.
- Ao escolher entre duas abordagens defensáveis, apresente o trade-off e deixe o
  usuário decidir em vez de escolher silenciosamente.
- Prefira passos pequenos e verificáveis (implementar → rodar → commitar) a despejar
  vários arquivos de uma vez.

## Registro de decisões (ADR)

`docs/adr/` é o diário de decisões que sustentam a defesa técnica (§ 6). O agente
mantém esse diretório atualizado:

Estado: **0001–0016 aceitos e implementados** (layout/stack, lock, erros, deletes,
filtros, unicidade, CNPJ, testes, auth, front-end separado, grupo opcional e seed
do leitor). Decisão nova ou alterada gera ADR novo — nunca reescreva um aceito.

- **Detecte a decisão.** Toda escolha entre alternativas defensáveis — modelagem,
  `ON DELETE`, transação/lock, estratégia de erro, autenticação, layout de pastas,
  ferramental — é candidata a ADR.
- **Pergunte antes de criar.** O agente nunca cria um ADR silenciosamente:
  apresenta a proposta (contexto, opções, recomendação, consequências) e aguarda
  confirmação explícita do usuário.
- **Formato.** `docs/adr/NNNN-titulo-curto-em-kebab.md`, numeração sequencial, em
  pt-BR: título (`# ADR-000N: ...`), **Data**, **Status** (`proposto` | `aceito` |
  `substituído por ADR-XXXX`), **Contexto**, **Decisão**, **Alternativas
  consideradas**, **Consequências**.
- **Decisão mudou?** Não reescreva um ADR aceito: crie um novo ADR que o substitui
  e atualize o status do antigo.
- **Sincronize.** A decisão aceita deve aparecer em `specs/SPEC.md` (seção
  Decisions) e, quando não óbvia, em um comentário no código (§ 2.g).

## Definition of Done

Uma tarefa só está pronta quando:

- [ ] o comportamento segue o enunciado e não viola nenhum invariante de domínio;
- [ ] lint/format (`ruff`) e testes passam (`uv run pytest`);
- [ ] mudanças de schema têm migration Alembic correspondente;
- [ ] endpoints novos/alterados estão documentados no OpenAPI **e** no README;
- [ ] a decisão não óbvia está registrada (comentário justificando + `specs/` quando existir);
- [ ] o commit segue Conventional Commits e o histórico continua incremental.
