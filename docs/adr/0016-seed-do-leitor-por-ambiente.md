# ADR-0016: Seed do usuário leitor por variáveis de ambiente

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O seed (`uv run python -m app.seed`) cria apenas o admin a partir de
`ADMIN_EMAIL`/`ADMIN_PASSWORD`; não existe rota pública de cadastro de usuário
(decisão do ADR-0013, § 3.a). Para demonstrar o 403 de escrita na UI ao vivo — e
não só na suíte — é preciso conseguir logar com um usuário de perfil leitor.

## Decisão

- Generalizar `app/services/usuarios.criar_admin_se_nao_existir` para
  `criar_usuario_se_nao_existir(session, *, nome, email, senha, perfil)`, mantendo
  a idempotência por e-mail e a normalização de caixa.
- `app/seed.py` passa a semear admin e leitor a partir do ambiente
  (`ADMIN_EMAIL`/`ADMIN_PASSWORD`, `LEITOR_EMAIL`/`LEITOR_PASSWORD`), pulando cada
  um quando as variáveis estiverem ausentes; a saída do comando informa o resultado.
- `.env.example` ganha as duas variáveis novas, com valores de exemplo — sem
  credencial real no repositório.

## Alternativas consideradas

- Admin-only — o 403 fica coberto só por testes; a demonstração ao vivo do
  diferencial perde valor e o plano do front pede a demo.
- Credenciais fixas no código/seed — inaceitável: segredo no repositório.
- Rota de cadastro de usuários — funcionalidade fora do enunciado e superfície de
  ataque nova; descartada.

## Consequências

- Demo do 403 ao vivo com `LEITOR_EMAIL`/`LEITOR_PASSWORD` no `.env` local.
- Diff pequeno em `app/services/usuarios.py` e `app/seed.py`, com
  `tests/test_seed.py` atualizado para os dois perfis. Sem migration: a tabela
  `usuarios` já existe.
