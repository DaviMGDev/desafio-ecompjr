"""Rotas do painel — uma tela por módulo, todas atrás do login.

Cada módulo expõe um `ar = APIRouter()` que o `frontend/main.py` monta no app.
Rotas de escrita repetem a checagem de perfil: a UI esconde os controles do
leitor, mas a rota não confia no cliente (a API também responde 403).
"""

from fasthtml.common import FtResponse, Redirect

from frontend import sessao

SEM_PERMISSAO = "Perfil sem permissão de escrita."


def redirecionar_ao_login(sess):
    """Limpa a sessão local e volta ao login (a API recusou o token)."""
    sessao.sair(sess)
    return Redirect("/login")


def resposta_403(conteudo):
    """403 com a região da tela renderizada, para o leitor não perder a página."""
    return FtResponse(conteudo, status_code=403)
