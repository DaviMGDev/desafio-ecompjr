"""Login e logout — as únicas rotas públicas do painel."""

from fasthtml.common import H1, APIRouter, Button, Form, Main, Redirect, Section, Span

from frontend import api, sessao
from frontend.componentes import alerta, campo

ar = APIRouter()


def _tela(erro: str | None = None, email: str = ""):
    """Formulário de entrada (o erro do 401 aparece acima dos campos)."""
    return (
        Main(
            Section(
                H1(
                    Span("愚公移山 Variedades", cls="marca-login"),
                    Span("Painel de estoque", cls="subtitulo"),
                ),
                alerta("erro", erro) if erro else None,
                Form(
                    campo(
                        "E-mail",
                        "email",
                        tipo="email",
                        valor=email,
                        required=True,
                        autocomplete="username",
                        autofocus=True,
                    ),
                    campo(
                        "Senha",
                        "senha",
                        tipo="password",
                        required=True,
                        autocomplete="current-password",
                    ),
                    Button("Entrar", type="submit", cls="primario"),
                    method="post",
                    action="/login",
                    cls="form-login",
                ),
                cls="login-cartao",
            ),
            cls="conteudo conteudo-estreito",
        ),
    )


@ar("/login", methods=["GET"])
def pagina_login(sess):
    """Mostra o formulário; quem já tem sessão vai direto ao painel."""
    if sessao.autenticado(sess):
        return Redirect("/produtos")
    return _tela()


@ar("/login", methods=["POST"])
def entrar_painel(email: str = "", senha: str = "", sess=None):
    """Troca as credenciais pelo token da API e abre a sessão do painel."""
    status, corpo = api.login(email, senha)
    if status == 200:
        sessao.entrar(sess, corpo["access_token"])
        return Redirect("/produtos")

    mensagem = (
        api.mensagem_do_detail(api.detail_do_corpo(corpo))
        if corpo
        else "Não foi possível falar com a API."
    )
    return _tela(erro=mensagem, email=email)


@ar("/logout", methods=["GET", "POST"])
def sair_painel(sess):
    """Limpa a sessão do painel (o token deixa de ser usado).

    GET também é atendido para quem chega pela URL; o botão usa POST.
    """
    sessao.sair(sess)
    return Redirect("/login")
