# ADR-0013: Borda de autenticação — argon2 + JWT HS256 com `sub` = id

**Data:** 2026-09-30
**Status:** aceito

## Contexto

O diferencial de autenticação (§ 3.a) foi implementado no formato mínimo definido
no ADR-0008; faltavam ainda as escolhas de biblioteca de hash, algoritmo do JWT
e conteúdo do payload.

## Decisão

- hash de senha **argon2** via `pwdlib` (`PasswordHash.recommended()`);
- **JWT HS256** com PyJWT: `sub` = id do usuário, `perfil` e `exp`;
- segredo (`JWT_SECRET`) do ambiente, com 32+ bytes (o exemplo e o default já
  seguem esse tamanho);
- validação do token em dependency (`usuario_atual`) e autorização de escrita em
  dependency separada (`exigir_admin`).

## Alternativas consideradas

- `passlib`/bcrypt — manutenção incerta e avisos de compatibilidade; `pwdlib` é
  a recomendação atual do ecossistema FastAPI.
- RS256 (chave assimétrica) — desnecessário para um serviço único que assina e
  verifica os próprios tokens.
- `sub` = e-mail — trocar o e-mail invalidaria sessões sem motivo.

## Consequências

- Dependências modernas e mantidas; senha nunca armazenada em claro.
- Trocar o e-mail do usuário não invalida tokens emitidos.
- Segredo curto gera aviso do PyJWT — resolvido ao alongar o valor de exemplo.
