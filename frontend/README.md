# Painel de estoque — front-end FastHTML

Painel web da loja **愚公移山 Variedades**. É um serviço à parte (ADR-0014):
consome a API de Gerenciamento de Estoque por HTTP e **não altera o backend** —
routers, models e services continuam exatamente como estão.

- **Visual:** `specs/DESIGN.md` (tokens "Chá & Jade"; Pico CSS mapeado em
  `frontend/static/css/app.css`).
- **Estrutura das telas:** `specs/layout/*.layout.txt` (LAYOUT v1, uma tela por
  arquivo) — o contrato que a implementação segue.

## Como rodar

```bash
docker compose up -d db                              # PostgreSQL
uv run uvicorn app.main:app --reload                 # API em :8000
uv run python -m app.seed                            # admin (e leitor, se LEITOR_* no .env)
uv run --group frontend python -m frontend.main      # painel em :5001
```

Abra <http://localhost:5001> e entre com o admin do `.env`. As dependências do
painel vivem no grupo opcional `frontend` do `pyproject.toml` (ADR-0015): o
`requirements.txt` gerado e o install da API não mudam.

Também funciona via uvicorn direto (útil para depurar):

```bash
uv run --group frontend uvicorn frontend.main:app --reload --port 5001
```

## Variáveis de ambiente (`.env`)

| Variável | Padrão | Para que serve |
|---|---|---|
| `API_URL` | `http://localhost:8000` | Base da API consumida pelo painel |
| `SESSION_SECRET` | valor de dev | Assina o cookie de sessão (separado do `JWT_SECRET`) |
| `SESSION_COOKIE` | `painel_sessao` | Nome do cookie de sessão |
| `LEITOR_EMAIL` / `LEITOR_PASSWORD` | — | Se definidos, o seed cria o usuário de leitura (perfil leitor) |

O token da API fica **dentro do cookie de sessão assinado**; o navegador não
carrega bearer token em JavaScript (ADR-0014).

## Telas

| Rota | Tela | Cobre da API |
|---|---|---|
| `GET /login` | Entrada (+ estado de erro do 401) | `POST /auth/login` |
| `GET /produtos` | Lista com filtros, criar/editar/excluir, "carregar mais" | `/produtos`, `/categorias`, `/fornecedores` |
| `GET /estoque-baixo` | Consulta avançada (`saldo <= mínimo`) | `GET /produtos/estoque-baixo` |
| `GET /movimentacoes` | Filtros + registro + histórico imutável | `/movimentacoes`, `/produtos/{id}` |
| `GET /fornecedores` | Lista com filtro e CRUD | `/fornecedores` |
| `GET /categorias` | Lista e CRUD | `/categorias` |

`POST /logout` encerra a sessão local; `/` redireciona para `/produtos`.

Com perfil **leitor**, os controles de escrita (formulários, Editar, Excluir,
Registrar) não são renderizados — não ficam desabilitados. Erros da API chegam
como o `detail` do envelope: 409/404 em alerta, 422 por campo.

## Testes

```bash
uv run --group frontend pytest frontend/tests
```

Os testes dirigem o app FastHTML com `fasthtml.common.Client` (`HX-Request`
quando o fluxo é parcial) e apontam o cliente HTTP do painel para o app ASGI da
API, reutilizando a fixture transacional do ADR-0012 — sem servidor real.

## Estrutura

```
frontend/
  main.py          # fast_app, beforeware de login e montagem dos routers
  api.py           # cliente httpx da API (única saída de rede)
  sessao.py        # token/perfil na sessão assinada
  componentes.py   # shell, campos, alertas, selos, listas
  rotas/           # uma tela por módulo (login, produtos, ...)
  static/          # css/ e js/ vendorizados (Pico 2.5 e htmx 2.0.7)
  tests/           # testes de tela com a API em ASGI
```

Os assets em `static/` são servidos pelo próprio painel (sem CDN em runtime):
Pico CSS v2.5 (MIT) e htmx 2.0.7 (BSD 2-clause), com os avisos de licença
originais nos arquivos.

## Decisões

- ADR-0014 — painel como serviço ASGI separado consumindo a API; JWT em cookie
  de sessão assinado.
- ADR-0015 — dependências do painel em grupo opcional do `pyproject.toml`.
- ADR-0016 — seed do leitor por `LEITOR_EMAIL`/`LEITOR_PASSWORD` para a demo do
  403.
