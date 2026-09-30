"""Tela de estoque baixo — consulta avançada (saldo <= mínimo), só leitura."""

from typing import Any

from fasthtml.common import H1, A, APIRouter, Div, P, Redirect, Span

from frontend import api, sessao
from frontend.componentes import alerta, botao, cartao, estado_vazio, indicador, selo, shell
from frontend.rotas import redirecionar_ao_login
from frontend.rotas.catalogos import nome_por_id, opcoes_categorias, opcoes_fornecedores

ar = APIRouter()

LIMITE_PADRAO = 20
LIMITE_MAXIMO = 100
CARREGANDO = "carregando-estoque-baixo"


def _buscar(sess, limite: int):
    """Devolve `(produtos, erro)`, onde erro é Redirect ou alerta renderizável."""
    status, corpo = api.produtos_estoque_baixo(sessao.token_da_sessao(sess), limit=limite, offset=0)
    if status == 401:
        return None, redirecionar_ao_login(sess)
    if status != 200:
        return None, alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo)))
    return corpo, None


def _resumo(produtos: list[dict[str, Any]]):
    """Faixa de resumo com a contagem de itens críticos."""
    if not produtos:
        return None
    if len(produtos) == 1:
        return alerta("critico", "1 produto precisa de reposição")
    return alerta("critico", f"{len(produtos)} produtos precisam de reposição")


def _lista(
    produtos: list[dict[str, Any]],
    limite: int,
    pode_escrever: bool,
    catalogo_categorias: list[tuple[str, str]],
    catalogo_fornecedores: list[tuple[str, str]],
):
    """Itens críticos, com atalho de entrada só para quem pode escrever."""
    if not produtos:
        return estado_vazio("Nenhum produto abaixo do mínimo")

    itens = []
    for produto in produtos:
        acao = (
            Div(
                A(
                    "Registrar entrada",
                    href=f"/movimentacoes?produto_id={produto['id']}",
                    role="button",
                    cls="secundario pequeno",
                ),
                cls="acoes",
            )
            if pode_escrever
            else None
        )
        itens.append(
            Div(
                Div(
                    Span(produto["nome"], cls="item-titulo"),
                    Span(f"SKU {produto['sku']}", cls="item-meta mono"),
                    cls="item-principal",
                ),
                Span(
                    f"Categoria: {nome_por_id(catalogo_categorias, produto['categoria_id'])}",
                    cls="item-meta",
                ),
                Span(
                    f"Fornecedor: {nome_por_id(catalogo_fornecedores, produto['fornecedor_id'])}",
                    cls="item-meta",
                ),
                Span(f"Estoque: {produto['quantidade_em_estoque']}", cls="item-saldo"),
                Span(f"Mínimo: {produto['quantidade_minima']}", cls="item-meta mono"),
                selo("critico", "Crítico"),
                acao,
                cls="item",
            )
        )
    return Div(
        Div(*itens, cls="lista"), indicador(CARREGANDO), _carregar_mais(limite, len(produtos))
    )


def _carregar_mais(limite: int, quantidade: int):
    """Botão que amplia a lista (limit/offset da API)."""
    if quantidade < limite or limite >= LIMITE_MAXIMO:
        return None
    return botao(
        "Carregar mais",
        "secundario",
        hx_get="/estoque-baixo/lista",
        hx_indicator=f"#{CARREGANDO}",
        hx_vals=f'{{"limite": {min(limite + LIMITE_PADRAO, LIMITE_MAXIMO)}}}',
        hx_target="#cartao-lista-estoque-baixo",
        hx_swap="outerHTML",
    )


def _cartao_lista(
    sess,
    limite: int,
    produtos: list[dict[str, Any]] | None = None,
    erro=None,
):
    """Cartão da lista crítica (ou do erro) — alvo do "carregar mais"."""
    if produtos is None and erro is None:
        produtos, erro = _buscar(sess, limite)
        if isinstance(erro, Redirect):
            return erro
    catalogo_categorias = opcoes_categorias(sess)
    catalogo_fornecedores = opcoes_fornecedores(sess)
    return cartao(
        erro
        if erro is not None
        else _lista(
            produtos,
            limite,
            sessao.eh_admin(sess),
            catalogo_categorias,
            catalogo_fornecedores,
        ),
        indicador(CARREGANDO),
        titulo="Produtos no/abaixo do mínimo",
        id_="cartao-lista-estoque-baixo",
    )


@ar("/estoque-baixo", methods=["GET"])
def tela_estoque_baixo(sess):
    """Página completa: resumo e lista dos produtos críticos."""
    produtos, erro = _buscar(sess, LIMITE_PADRAO)
    if isinstance(erro, Redirect):
        return erro

    return shell(
        H1("Estoque baixo"),
        P("Produtos no ou abaixo do estoque mínimo.", cls="subtitulo-pagina"),
        _resumo(produtos),
        _cartao_lista(sess, LIMITE_PADRAO, produtos=produtos, erro=erro),
        sess=sess,
        atual="/estoque-baixo",
        nome_pagina="Estoque baixo",
    )


@ar("/estoque-baixo/lista", methods=["GET"])
def lista_estoque_baixo(sess, limite: int = LIMITE_PADRAO):
    """Cartão da lista com mais itens — alvo do "carregar mais"."""
    limite = max(LIMITE_PADRAO, min(int(limite), LIMITE_MAXIMO))
    return _cartao_lista(sess, limite)
