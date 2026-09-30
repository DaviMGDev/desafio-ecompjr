"""Sessão do painel: o JWT fica no cookie assinado, o navegador não vê o token.

O cookie é do Starlette (`SessionMiddleware`, assinado com `SESSION_SECRET`);
o perfil lido do payload decide apenas o que a UI mostra — quem autoriza de
verdade continua sendo a API (ADR-0014 e ADR-0016).
"""

import jwt
from fasthtml.common import Redirect

CHAVE_TOKEN = "token"
CHAVE_PERFIL = "perfil"


def perfil_do_token(token: str) -> str:
    """Lê o perfil do payload do JWT sem verificar a assinatura (uso de UI)."""
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
    except jwt.InvalidTokenError:
        return ""
    return str(payload.get("perfil", ""))


def entrar(sess, token: str) -> None:
    """Guarda o token e o perfil na sessão assinada."""
    sess[CHAVE_TOKEN] = token
    sess[CHAVE_PERFIL] = perfil_do_token(token)


def sair(sess) -> None:
    """Limpa a sessão (logout local; a API não tem rota de logout)."""
    sess.pop(CHAVE_TOKEN, None)
    sess.pop(CHAVE_PERFIL, None)


def token_da_sessao(sess) -> str | None:
    """Token guardado na sessão, se houver."""
    return sess.get(CHAVE_TOKEN)


def perfil_da_sessao(sess) -> str:
    """Perfil do usuário logado (`admin` ou `leitor`); vazio se anônimo."""
    return str(sess.get(CHAVE_PERFIL, ""))


def eh_admin(sess) -> bool:
    """Diz se o usuário logado pode escrever — a UI esconde, a API decide."""
    return perfil_da_sessao(sess) == "admin"


def autenticado(sess) -> bool:
    """Há token na sessão?"""
    return bool(token_da_sessao(sess))


def exigir_login(req, sess):
    """Beforeware do painel: sem token, volta ao login (rota pública)."""
    if not autenticado(sess):
        return Redirect("/login")
