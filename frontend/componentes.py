"""Componentes compartilhados: o shell, campos de formulário e estados visuais."""

from fasthtml.common import (
    A,
    Button,
    Div,
    Footer,
    Form,
    Header,
    Input,
    Label,
    Main,
    Nav,
    Option,
    P,
    Select,
    Small,
    Span,
    Textarea,
    Title,
)

from frontend.config import settings
from frontend.sessao import perfil_da_sessao

NAVEGACAO = (
    ("Produtos", "/produtos"),
    ("Estoque baixo", "/estoque-baixo"),
    ("Movimentações", "/movimentacoes"),
    ("Fornecedores", "/fornecedores"),
    ("Categorias", "/categorias"),
)

ROTULO_PERFIL = {"admin": "Administrador", "leitor": "Leitor"}

ICONE = (
    "data:image/svg+xml,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
    "<text y='0.9em' font-size='90'>⛰️</text></svg>"
)


def pagina(nome: str) -> Title:
    """Título da aba, sempre com o nome do painel."""
    return Title(f"{nome} · Painel 愚公移山 Variedades")


def shell(*conteudo, sess, atual: str = "", nome_pagina: str = ""):
    """Casca comum: cabeçalho com navegação, conteúdo e rodapé."""
    links = [
        A(
            rotulo,
            href=destino,
            cls="ativo" if destino == atual else None,
            aria_current="page" if destino == atual else None,
        )
        for rotulo, destino in NAVEGACAO
    ]
    usuario = ROTULO_PERFIL.get(perfil_da_sessao(sess), "Sessão")
    return (
        pagina(nome_pagina),
        Header(
            A("愚公移山 Variedades", href="/produtos", cls="marca"),
            Nav(*links, cls="menu", aria_label="Seções do painel"),
            Div(
                Span(usuario, cls="usuario"),
                Form(
                    Button("Sair", type="submit", cls="secundario pequeno"),
                    method="post",
                    action="/logout",
                    cls="form-sair",
                ),
                cls="conta",
            ),
            cls="topo",
        ),
        Main(*conteudo, cls="conteudo"),
        Footer(
            Span("Painel de estoque — contrato da API em "),
            A(f"{settings.api_url}/docs", href=f"{settings.api_url}/docs", cls="link-api"),
            cls="rodape",
        ),
    )


def alerta(tipo: str, mensagem: str, *, id_: str | None = None, oob: bool = False):
    """Faixa de erro/sucesso/criticidade; `oob` troca o elemento fora do alvo."""
    attrs: dict = {"cls": f"alerta alerta-{tipo}", "role": "alert"}
    if id_:
        attrs["id"] = id_
    if oob:
        attrs["hx_swap_oob"] = "outerHTML" if not id_ else f"outerHTML:#{id_}"
    return Div(Span(mensagem), **attrs)


def campo(
    rotulo: str,
    nome: str,
    *,
    tipo: str = "text",
    valor: str | int | None = None,
    erro: str | None = None,
    **attrs,
) -> Label:
    """Campo rotulado, com mensagem de erro por campo quando houver."""
    return Label(
        Span(rotulo, cls="rotulo"),
        Input(
            name=nome,
            type=tipo,
            value=valor,
            aria_invalid="true" if erro else None,
            **attrs,
        ),
        Small(erro, cls="erro-campo") if erro else None,
        cls="campo campo-com-erro" if erro else "campo",
    )


def opcoes_select(opcoes: list[tuple[str, str]], valor: object) -> list[Option]:
    """Opções de um select, marcando a escolhida."""
    return [
        Option(rotulo, value=valor_opcao, selected=str(valor_opcao) == str(valor))
        for valor_opcao, rotulo in opcoes
    ]


def select_campo(
    rotulo: str,
    nome: str,
    opcoes: list[tuple[str, str]],
    *,
    valor: object = None,
    erro: str | None = None,
    vazio: str = "Selecione…",
    vazio_desabilitado: bool = True,
    **attrs,
) -> Label:
    """Select rotulado; o primeiro item vazio serve de placeholder ou "Todos"."""
    itens = []
    if vazio:
        itens.append(Option(vazio, value="", disabled=vazio_desabilitado, selected=not valor))
    itens.extend(opcoes_select(opcoes, valor))
    return Label(
        Span(rotulo, cls="rotulo"),
        Select(*itens, name=nome, aria_invalid="true" if erro else None, **attrs),
        Small(erro, cls="erro-campo") if erro else None,
        cls="campo campo-com-erro" if erro else "campo",
    )


def campo_longo(
    rotulo: str,
    nome: str,
    *,
    valor: str = "",
    erro: str | None = None,
    **attrs,
) -> Label:
    """Campo de texto longo (textarea) com rótulo e mensagem de erro."""
    return Label(
        Span(rotulo, cls="rotulo"),
        Textarea(valor or "", name=nome, aria_invalid="true" if erro else None, **attrs),
        Small(erro, cls="erro-campo") if erro else None,
        cls="campo campo-com-erro" if erro else "campo",
    )


def botao(texto: str, variante: str = "primario", **attrs) -> Button:
    """Botão com a variante visual (`primario`, `secundario`, `danger`, `ghost`)."""
    return Button(texto, cls=variante, **attrs)


def selo(tipo: str, texto: str) -> Span:
    """Selo de estado: `entrada`, `saida` ou `critico`."""
    return Span(texto, cls=f"selo selo-{tipo}")


def estado_vazio(mensagem: str):
    """Bloco de lista vazia."""
    return Div(P(mensagem, cls="vazio"), cls="vazio-caixa")


def indicador(id_: str):
    """Texto de carregamento que o HTMX mostra durante uma requisição."""
    return Span("Carregando…", id=id_, cls="carregando htmx-indicator")


def cartao(*conteudo, titulo: str | None = None, cls: str = "", id_: str | None = None):
    """Cartão de seção, com título e id opcionais (o id é o alvo do HTMX)."""
    filhos = [Span(titulo, cls="cartao-titulo")] if titulo else []
    attrs: dict = {"cls": f"cartao {cls}".strip()}
    if id_:
        attrs["id"] = id_
    return Div(*filhos, *conteudo, **attrs)
