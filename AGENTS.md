# desafio-ecompjr — API de Gerenciamento de Estoque

> Desafio técnico da Trilha Back-End Prosel 2026.2 (EcompJr/UEFS): uma API em
> **FastAPI + PostgreSQL** para cadastro de fornecedores, produtos e categorias e
> para auditoria de movimentações de estoque.
>
> **Status atual: repositório sem código.** Ainda não existe `pyproject.toml`,
> `app/`, migrations ou banco. Este arquivo descreve o alvo; comandos abaixo são
> o contrato esperado depois do bootstrap.

## Fonte da verdade

| Caminho | Papel |
|---|---|
| `desafio-tecnico-backend-prosel-2026.2/desafio-tecnico-backend-prosel-2026.2.md` | Enunciado oficial (**read-only** — nunca editar) |
| `specs/` | Especificações do projeto (a criar pelo candidato; domínio, features BDD e decisões em prosa) |
| `docs/adr/` | ADRs — decisões técnicas explicáveis na defesa (ver *Registro de decisões (ADR)*) |
| `README.md` | Documentação de entrega (setup, rotas, exemplos) — ainda não existe |

Em caso de conflito entre um `specs/*` e o enunciado, o **enunciado vence**.
Não invente requisitos: se algo não está no enunciado, marque como decisão de projeto.

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
- Camadas/estrutura de diretórios: **em aberto**. Não imponha uma arquitetura antes
  de o usuário decidir; proponha opções, registre a escolha e siga o padrão já existente.

Toda decisão relevante (transações, locks, estratégia de erro, modelagem de
relacionamentos) deve ser explicável em voz alta — haverá **defesa técnica** (§ 6).

## Comandos

Fluxo principal (`uv`):

```bash
uv sync                                   # instala deps do pyproject + lock
uv run uvicorn app.main:app --reload      # sobe a API em dev
uv run alembic revision --autogenerate -m "cria tabela produtos"
uv run alembic upgrade head               # aplica migrations
uv run pytest -q                          # testes
uv run ruff check . && uv run ruff format .
```

Compatibilidade com `pip` (para quem for avaliar sem `uv`):

```bash
uv export --no-hashes -o requirements.txt   # regenerar SEMPRE que mexer em deps
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

- `requirements.txt` é **artefato gerado** — nunca edite à mão; se o fluxo mudar,
  ele é regenerado pelo `uv export`.
- Banco local: subir via Docker/Postgres é decisão pendente; se existir
  `docker-compose.yml`, documente o comando no README.
- Nunca commite `.env`, `venv/`, `__pycache__/`, dumps de banco ou credenciais.

## Invariantes de domínio

Resumo operacional — os detalhes ficam em `specs/` quando existir. Nunca viole:

1. **Movimentação de estoque é imutável**: só `POST` e leitura. Não crie rota de
   `PUT`/`PATCH`/`DELETE` para movimentações, nem permita alterá-las por efeito colateral.
2. **Toda movimentação atualiza o saldo do produto na mesma transação** que a insere;
   se o saldo ficar negativo e isso for inválido, a transação inteira falha.
3. **Categoria com produtos vinculados não pode ser excluída** (§ 2.c) — responda com erro claro, não com 500.
4. **Unicidade garantida no banco**, não apenas na aplicação: `produto.sku`,
   `fornecedor.cnpj`, `fornecedor.email`, `categoria.nome`.
5. **Integridade referencial** explícita (FKs + política de `ON DELETE`) — decida e justifique.
6. **Consulta avançada é requisito obrigatório**: produtos em/abaixo do estoque mínimo
   e filtro de movimentações por período e/ou fornecedor.
7. **Erros padronizados**: modelo de resposta único, HTTP correto
   (400/404/409/422 conforme o caso, 500 para falhas internas), **sem stack trace** e
   **sem 200 em requisição falha**.

## Erros, validação e documentação da API

- Use `HTTPException`/exception handlers do FastAPI com um schema de erro único
  (`{"detail": ...}` ou envelope próprio — decida e documente).
- Validação de entrada via Pydantic; não valide à mão o que o schema já garante.
- Cada endpoint precisa de: método, path, query/path params, body de exemplo,
  respostas 2xx e 4xx/5xx **com JSON de exemplo** — no OpenAPI (docstrings/`responses=`)
  e espelhado no `README.md`. Collection Postman/Insomnia é opcional e complementar.

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

- `pytest` + `fastapi.testclient`/`httpx`, com fixtures de banco isoladas
  (transação revertida por teste) — sem depender de ordem de execução.
- Cubra as regras de negócio, não só o caminho feliz: imutabilidade da movimentação,
  exclusão de categoria com produtos, unicidade de `cnpj`/`email`/`sku`, saldo após entrada/saída.
- Workflow de CI (GitHub Actions) rodando lint + testes em cada push é esperado (§ 3.b).

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
