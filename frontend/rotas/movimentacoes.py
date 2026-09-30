"""Tela de movimentações — histórico imutável (sem editar/excluir) e registro.

O registro é a única escrita; a região volta com o saldo do produto atualizado
(buscado de novo na API), conforme o contrato em `specs/layout`.
"""

from datetime import datetime
from typing import Any

from fasthtml.common import H1, APIRouter, Div, Form, Redirect, Span

from frontend import api, sessao
from frontend.componentes import (
    alerta,
    botao,
    campo,
    campo_longo,
    cartao,
    estado_vazio,
    indicador,
    select_campo,
    selo,
    shell,
)
from frontend.rotas import SEM_PERMISSAO, redirecionar_ao_login, resposta_403
from frontend.rotas.catalogos import nome_por_id, opcoes_fornecedores, opcoes_produtos

ar = APIRouter()

REGIAO = "conteudo-movimentacoes"
FILTROS = "filtros-movimentacoes"
CARREGANDO = "carregando-historico"
LIMITE_PADRAO = 20
LIMITE_MAXIMO = 100

OPCOES_TIPO = [("entrada", "Entrada"), ("saida", "Saída")]


def _inteiro(valor: Any) -> int | None:
    """Converte o valor do formulário em inteiro, tolerando vazio."""
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return None


def _data_legivel(valor: str) -> str:
    """Formata o `data` ISO da API no padrão pt-BR (horário local)."""
    try:
        return datetime.fromisoformat(valor).astimezone().strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return valor


def _saldo_de(sess, produto_id: Any) -> str:
    """Texto do saldo atual de um produto (buscado na API), ou traço."""
    identificador = _inteiro(produto_id)
    if not identificador:
        return "Saldo atual: —"
    status, corpo = api.obter_produto(sessao.token_da_sessao(sess), identificador)
    if status != 200:
        return "Saldo atual: —"
    return f"Saldo atual: {corpo['quantidade_em_estoque']}"


def _form(
    sess,
    *,
    produto_id: Any = "",
    tipo: str = "entrada",
    quantidade: Any = "",
    fornecedor_id: Any = "",
    observacao: str = "",
    erros: dict[str, str] | None = None,
) -> Form:
    """Formulário de registro de movimentação (entrada/saída)."""
    erros = erros or {}
    return Form(
        select_campo(
            "Produto",
            "produto_id",
            opcoes_produtos(sess),
            valor=produto_id,
            erro=erros.get("produto_id"),
            required=True,
            hx_get="/movimentacoes/saldo",
            hx_trigger="change",
            hx_target="#saldo-atual",
            hx_swap="outerHTML",
        ),
        Span(_saldo_de(sess, produto_id), id="saldo-atual", cls="saldo"),
        select_campo(
            "Tipo",
            "tipo",
            OPCOES_TIPO,
            valor=tipo,
            erro=erros.get("tipo"),
            vazio="",
            required=True,
        ),
        campo(
            "Quantidade",
            "quantidade",
            tipo="number",
            valor=quantidade,
            erro=erros.get("quantidade"),
            required=True,
            min="1",
            step="1",
        ),
        select_campo(
            "Fornecedor",
            "fornecedor_id",
            opcoes_fornecedores(sess),
            valor=fornecedor_id,
            erro=erros.get("fornecedor_id"),
        ),
        campo_longo("Observação", "observacao", valor=observacao, maxlength=255, rows=3),
        Div(botao("Registrar", "primario", type="submit"), cls="filtros-acoes"),
        id="form-movimentacao",
        hx_include=f"#{FILTROS}",
        hx_indicator=f"#{CARREGANDO}",
        hx_post="/movimentacoes",
        hx_target=f"#{REGIAO}",
        hx_swap="outerHTML",
        method="post",
        action="/movimentacoes",
        cls="formulario",
    )


def _filtros(
    sess,
    *,
    produto_id: str = "",
    tipo: str = "",
    fornecedor_id: str = "",
    data_inicio: str = "",
    data_fim: str = "",
) -> Form:
    """Recortes da API: produto, tipo, fornecedor e período inclusivo."""
    return Form(
        select_campo(
            "Produto",
            "filtro_produto_id",
            opcoes_produtos(sess),
            valor=produto_id,
            vazio="Todos",
            vazio_desabilitado=False,
        ),
        select_campo(
            "Tipo",
            "filtro_tipo",
            OPCOES_TIPO,
            valor=tipo,
            vazio="Todos",
            vazio_desabilitado=False,
        ),
        select_campo(
            "Fornecedor",
            "filtro_fornecedor_id",
            opcoes_fornecedores(sess),
            valor=fornecedor_id,
            vazio="Todos",
            vazio_desabilitado=False,
        ),
        campo("De", "filtro_data_inicio", tipo="date", valor=data_inicio),
        campo("Até", "filtro_data_fim", tipo="date", valor=data_fim),
        Div(
            botao("Filtrar", "secundario", type="submit"),
            botao(
                "Limpar",
                "ghost",
                type="button",
                hx_get="/movimentacoes/lista",
                hx_target="#cartao-historico",
                hx_swap="outerHTML",
            ),
            cls="filtros-acoes",
        ),
        id=FILTROS,
        cls="filtros",
        hx_get="/movimentacoes/lista",
        hx_indicator=f"#{CARREGANDO}",
        hx_target="#cartao-historico",
        hx_swap="outerHTML",
        method="get",
        action="/movimentacoes/lista",
    )


def _historico(
    movimentacoes: list[dict[str, Any]],
    limite: int,
    catalogo_produtos: list[tuple[str, str]],
    catalogo_fornecedores: list[tuple[str, str]],
):
    """Linhas do histórico; não existe editar nem excluir em lugar nenhum."""
    if not movimentacoes:
        return estado_vazio("Nenhuma movimentação no período")

    linhas = []
    for movimentacao in movimentacoes:
        entrada = movimentacao["tipo"] == "entrada"
        fornecedor = (
            nome_por_id(catalogo_fornecedores, movimentacao["fornecedor_id"])
            if movimentacao["fornecedor_id"]
            else "Sem fornecedor"
        )
        linhas.append(
            Div(
                Span(_data_legivel(movimentacao["data"]), cls="item-meta mono"),
                selo("entrada" if entrada else "saida", "Entrada" if entrada else "Saída"),
                Span(str(movimentacao["quantidade"]), cls="item-quantidade"),
                Span(
                    nome_por_id(catalogo_produtos, movimentacao["produto_id"], prefixo="Produto #"),
                    cls="item-titulo",
                ),
                Span(fornecedor, cls="item-meta"),
                Span(movimentacao["observacao"], cls="item-meta")
                if movimentacao["observacao"]
                else None,
                cls="item",
            )
        )
    return Div(Div(*linhas, cls="lista"), _carregar_mais(limite, len(movimentacoes)))


def _carregar_mais(limite: int, quantidade: int):
    """Botão que amplia o histórico mantendo os filtros ativos."""
    if quantidade < limite or limite >= LIMITE_MAXIMO:
        return None
    return botao(
        "Carregar mais",
        "secundario",
        hx_get="/movimentacoes/lista",
        hx_include=f"#{FILTROS}",
        hx_vals=f'{{"limite": {min(limite + LIMITE_PADRAO, LIMITE_MAXIMO)}}}',
        hx_target="#cartao-historico",
        hx_swap="outerHTML",
    )


def _buscar(
    sess,
    *,
    limite: int,
    filtro_produto_id: str,
    filtro_tipo: str,
    filtro_fornecedor_id: str,
    filtro_data_inicio: str,
    filtro_data_fim: str,
):
    """Devolve `(movimentacoes, erro)`, onde erro é Redirect ou alerta."""
    params: dict[str, Any] = {"limit": limite, "offset": 0}
    if filtro_produto_id:
        params["produto_id"] = filtro_produto_id
    if filtro_tipo:
        params["tipo"] = filtro_tipo
    if filtro_fornecedor_id:
        params["fornecedor_id"] = filtro_fornecedor_id
    # O input é `date`; a API filtra por instante — o fim inclui o dia inteiro.
    if filtro_data_inicio:
        params["data_inicio"] = f"{filtro_data_inicio}T00:00:00"
    if filtro_data_fim:
        params["data_fim"] = f"{filtro_data_fim}T23:59:59"

    status, corpo = api.listar_movimentacoes(sessao.token_da_sessao(sess), **params)
    if status == 401:
        return None, redirecionar_ao_login(sess)
    if status != 200:
        return None, alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo)))
    return corpo, None


def _cartao_historico(
    sess,
    *,
    limite: int = LIMITE_PADRAO,
    filtro_produto_id: str = "",
    filtro_tipo: str = "",
    filtro_fornecedor_id: str = "",
    filtro_data_inicio: str = "",
    filtro_data_fim: str = "",
    movimentacoes=None,
    erro=None,
):
    """Cartão do histórico (filtros + linhas) — alvo dos filtros e da paginação."""
    if movimentacoes is None and erro is None:
        movimentacoes, erro = _buscar(
            sess,
            limite=limite,
            filtro_produto_id=filtro_produto_id,
            filtro_tipo=filtro_tipo,
            filtro_fornecedor_id=filtro_fornecedor_id,
            filtro_data_inicio=filtro_data_inicio,
            filtro_data_fim=filtro_data_fim,
        )
        if isinstance(erro, Redirect):
            return erro

    return cartao(
        _filtros(
            sess,
            produto_id=filtro_produto_id,
            tipo=filtro_tipo,
            fornecedor_id=filtro_fornecedor_id,
            data_inicio=filtro_data_inicio,
            data_fim=filtro_data_fim,
        ),
        erro
        if erro is not None
        else _historico(movimentacoes, limite, opcoes_produtos(sess), opcoes_fornecedores(sess)),
        indicador(CARREGANDO),
        titulo="Histórico",
        id_="cartao-historico",
    )


def _regiao(
    sess,
    *,
    alerta_=None,
    form: Any | None = None,
    limite: int = LIMITE_PADRAO,
    filtro_produto_id: str = "",
    filtro_tipo: str = "",
    filtro_fornecedor_id: str = "",
    filtro_data_inicio: str = "",
    filtro_data_fim: str = "",
):
    """Região mutável da tela: aviso + formulário (admin) + histórico filtrado."""
    movimentacoes, erro = _buscar(
        sess,
        limite=limite,
        filtro_produto_id=filtro_produto_id,
        filtro_tipo=filtro_tipo,
        filtro_fornecedor_id=filtro_fornecedor_id,
        filtro_data_inicio=filtro_data_inicio,
        filtro_data_fim=filtro_data_fim,
    )
    if isinstance(erro, Redirect):
        return erro

    return Div(
        alerta_,
        cartao(
            form if form is not None else _form(sess),
            titulo="Registrar movimentação",
            id_="cartao-form-movimentacao",
        )
        if sessao.eh_admin(sess)
        else None,
        _cartao_historico(
            sess,
            limite=limite,
            filtro_produto_id=filtro_produto_id,
            filtro_tipo=filtro_tipo,
            filtro_fornecedor_id=filtro_fornecedor_id,
            filtro_data_inicio=filtro_data_inicio,
            filtro_data_fim=filtro_data_fim,
            movimentacoes=movimentacoes,
            erro=erro,
        ),
        id=REGIAO,
    )


def _filtros_do_pedido(
    filtro_produto_id: str,
    filtro_tipo: str,
    filtro_fornecedor_id: str,
    filtro_data_inicio: str,
    filtro_data_fim: str,
) -> dict[str, str]:
    """Recorte ativo que acompanha uma escrita (hx-include dos filtros)."""
    return {
        "filtro_produto_id": filtro_produto_id.strip(),
        "filtro_tipo": filtro_tipo.strip(),
        "filtro_fornecedor_id": filtro_fornecedor_id.strip(),
        "filtro_data_inicio": filtro_data_inicio.strip(),
        "filtro_data_fim": filtro_data_fim.strip(),
    }


@ar("/movimentacoes", methods=["GET"])
def tela_movimentacoes(sess, produto_id: str = ""):
    """Página completa; o produto pode vir pré-selecionado (estoque baixo)."""
    regiao = _regiao(sess, form=_form(sess, produto_id=produto_id))
    if isinstance(regiao, Redirect):
        return regiao
    return shell(
        H1("Movimentações"),
        regiao,
        sess=sess,
        atual="/movimentacoes",
        nome_pagina="Movimentações",
    )


@ar("/movimentacoes/lista", methods=["GET"])
def lista_movimentacoes(
    sess,
    filtro_produto_id: str = "",
    filtro_tipo: str = "",
    filtro_fornecedor_id: str = "",
    filtro_data_inicio: str = "",
    filtro_data_fim: str = "",
    limite: int = LIMITE_PADRAO,
):
    """Cartão do histórico filtrado — alvo dos filtros e do "carregar mais"."""
    limite = max(LIMITE_PADRAO, min(int(limite), LIMITE_MAXIMO))
    return _cartao_historico(
        sess,
        limite=limite,
        filtro_produto_id=filtro_produto_id.strip(),
        filtro_tipo=filtro_tipo.strip(),
        filtro_fornecedor_id=filtro_fornecedor_id.strip(),
        filtro_data_inicio=filtro_data_inicio.strip(),
        filtro_data_fim=filtro_data_fim.strip(),
    )


@ar("/movimentacoes/saldo", methods=["GET"])
def saldo_do_produto(sess, produto_id: str = ""):
    """Saldo do produto selecionado no formulário (atualizado a cada troca)."""
    return Span(_saldo_de(sess, produto_id), id="saldo-atual", cls="saldo")


def _escrita_recusada(sess, filtros: dict[str, str]):
    """403 com a região quando o leitor força a rota de registro."""
    regiao = _regiao(sess, alerta_=alerta("erro", SEM_PERMISSAO), **filtros)
    if isinstance(regiao, Redirect):
        return regiao
    return resposta_403(regiao)


@ar("/movimentacoes", methods=["POST"])
def registrar_movimentacao(
    sess,
    produto_id: str = "",
    tipo: str = "entrada",
    quantidade: str = "",
    fornecedor_id: str = "",
    observacao: str = "",
    filtro_produto_id: str = "",
    filtro_tipo: str = "",
    filtro_fornecedor_id: str = "",
    filtro_data_inicio: str = "",
    filtro_data_fim: str = "",
):
    """Registra entrada/saída; 409 de saldo insuficiente aparece na hora."""
    filtros = _filtros_do_pedido(
        filtro_produto_id, filtro_tipo, filtro_fornecedor_id, filtro_data_inicio, filtro_data_fim
    )
    if not sessao.eh_admin(sess):
        return _escrita_recusada(sess, filtros)

    dados = {
        "produto_id": _inteiro(produto_id),
        "tipo": tipo,
        "quantidade": _inteiro(quantidade),
        "fornecedor_id": _inteiro(fornecedor_id),
        "observacao": observacao.strip() or None,
    }
    status, corpo = api.criar_movimentacao(sessao.token_da_sessao(sess), dados)
    if status == 401:
        return redirecionar_ao_login(sess)

    if status == 201:
        return _regiao(
            sess,
            alerta_=alerta("sucesso", "Movimentação registrada; saldo atualizado."),
            # mantém o produto selecionado para o saldo já aparecer atualizado
            form=_form(sess, produto_id=produto_id, tipo=tipo, fornecedor_id=fornecedor_id),
            **filtros,
        )

    erros = api.erros_por_campo(api.detail_do_corpo(corpo)) if status == 422 else None
    formulario = _form(
        sess,
        produto_id=produto_id,
        tipo=tipo,
        quantidade=quantidade,
        fornecedor_id=fornecedor_id,
        observacao=observacao,
        erros=erros,
    )
    if status == 422:
        return _regiao(
            sess,
            alerta_=alerta("erro", "Há campos inválidos."),
            form=formulario,
            **filtros,
        )
    return _regiao(
        sess,
        alerta_=alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo))),
        form=formulario,
        **filtros,
    )
