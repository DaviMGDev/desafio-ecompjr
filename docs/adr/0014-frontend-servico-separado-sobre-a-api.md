# ADR-0014: Frontend FastHTML como serviço ASGI separado consumindo a API

**Data:** 2026-09-30
**Status:** aceito

## Contexto

A UI não é exigida pelo enunciado (o barema avalia a API e o front-end está fora
do escopo da spec), mas o projeto decidiu construir uma para exercitar o contrato
público sem mexer no backend — em particular sem editar `app/main.py`, routers,
models ou services, conforme a regra de que uma necessidade de UI nunca força um
passe de edição na API.

Duas formas de servir a UI foram consideradas:

- (a) montar o app FastHTML dentro do FastAPI (`app.mount("/ui", ...)`) e chamar
  `app/services` diretamente;
- (b) um serviço ASGI próprio consumindo a API por HTTP (httpx).

## Decisão

- `frontend/` é um serviço ASGI FastHTML independente, servido em `:5001`, que
  fala com a API existente em `:8000` via httpx (JSON em pt-BR, envelope `detail`).
- O JWT do login fica na sessão assinada do front (cookie `httponly`); o navegador
  não recebe o token como bearer — o front injeta `Authorization` nas chamadas.
- 401 da API limpa a sessão e devolve o usuário ao login; escrever exige perfil
  admin (o controle de escrita nem aparece para o leitor).
- Login/logout são do próprio front, usando `POST /auth/login` para obter o token.

## Alternativas consideradas

- (a) montagem no FastAPI chamando services direto — um processo e sem hop HTTP,
  mas edita `app/main.py`, fura a superfície da API avaliada (a UI deixaria de
  provar que o contrato funciona) e duplicaria política de erro/transação fora
  dos routers.
- Proxy reverso (nginx/Caddy) unificando a UI e a API numa porta — peça de infra
  sem retorno em dev; o front fala server-side, então CORS nem entra na conversa.

## Consequências

- Dois processos em dev (`uvicorn app.main:app` + `frontend/main.py`); a API
  continua standalone e é ela que vai para a avaliação.
- O front consome exatamente o que qualquer app web/mobile consumiria — a
  integração passa a valer como teste de contrato.
- Testes do front usam `httpx.ASGITransport` contra `app.main` e reutilizam a
  fixture transacional do ADR-0012 — nada de servidor real na suíte.
- A sessão do front é assinada com segredo próprio (`SESSION_SECRET`), separado do
  `JWT_SECRET` da API; o cookie é assinado (não cifrado), mas o token dentro dele
  também é assinado pela API, então adulteração é detectada nos dois níveis.
