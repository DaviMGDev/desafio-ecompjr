"""Rotas do painel — uma tela por módulo, todas atrás do login.

Cada módulo expõe um `ar = APIRouter()` que o `frontend/main.py` monta no app.
Rotas de escrita repetem `exigir_admin`: a UI esconde os controles do leitor,
mas a rota não confia no cliente (a API também responde 403).
"""

from fasthtml.common import FtResponse

from frontend import sessao
from frontend.componentes import alerta


def proibido_para_leitor(sess):
    """Resposta 403 quando um leitor força uma rota de escrita."""
    if sessao.eh_admin(sess):
        return None
    return FtResponse(alerta("erro", "Perfil sem permissão de escrita."), status_code=403)
