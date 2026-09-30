"""Tela de produtos — lista com filtros e CRUD; saldo só muda por movimentação."""

from typing import Any

from fasthtml.common import H1, APIRouter, Div, Form, Input, Redirect, Span

from frontend import api, sessao
from frontend.componentes import (
    alerta,
    botao,
    campo,
    cartao,
    estado_vazio,
    indicador,
    select_campo,
    selo,
    shell,
)
from frontend.rotas import SEM_PERMISSAO, redirecionar_ao_login, resposta_403
from frontend.rotas.catalogos import nome_por_id, opcoes_categorias, opcoes_fornecedores

ar = APIRouter()

REGIAO = "conteudo-produtos"
CARREGANDO = "carregando-produtos"
FILTROS = "filtros-produtos"
LIMITE_PADRAO = 20
LIMITE_MAXIMO = 100


def _inteiro(valor: Any) -> int:
    """Converte o valor do formulário em inteiro, tolerando vazio."""
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return 0


def _form(
    *,
    nome: str = "",
    sku: str = "",
    preco_custo: str = "",
    preco_venda: str = "",
    quantidade_minima: Any = 0,
    categoria_id: Any = "",
    fornecedor_id: Any = "",
    produto_id: int | None = None,
    erros: dict[str, str] | None = None,
    opcoes_categorias: list[tuple[str, str]] | None = None,
    opcoes_fornecedores: list[tuple[str, str]] | None = None,
) -> Form:
    """Formulário de criar/editar produto — o mesmo componente nos dois modos."""
    erros = erros or {}
    editando = produto_id is not None
    destino = f"/produtos/{produto_id}" if editando else "/produtos"
    return Form(
        Input(type="hidden", name="produto_id", value=produto_id) if editando else None,
        campo("Nome", "nome", valor=nome, erro=erros.get("nome"), required=True, maxlength=120),
        campo("SKU", "sku", valor=sku, erro=erros.get("sku"), required=True, maxlength=64),
        campo(
            "Preço de custo",
            "preco_custo",
            tipo="number",
            valor=preco_custo,
            erro=erros.get("preco_custo"),
            required=True,
            step="0.01",
            min="0",
        ),
        campo(
            "Preço de venda",
            "preco_venda",
            tipo="number",
            valor=preco_venda,
            erro=erros.get("preco_venda"),
            required=True,
            step="0.01",
            min="0",
        ),
        campo(
            "Quantidade mínima",
            "quantidade_minima",
            tipo="number",
            valor=quantidade_minima,
            erro=erros.get("quantidade_minima"),
            min="0",
            step="1",
        ),
        select_campo(
            "Categoria",
            "categoria_id",
            opcoes_categorias or [],
            valor=categoria_id,
            erro=erros.get("categoria_id"),
            required=True,
        ),
        select_campo(
            "Fornecedor",
            "fornecedor_id",
            opcoes_fornecedores or [],
            valor=fornecedor_id,
            erro=erros.get("fornecedor_id"),
            required=True,
        ),
        Div(
            botao("Salvar", "primario", type="submit"),
            botao(
                "Cancelar",
                "ghost",
                type="button",
                hx_get="/produtos/novo",
                hx_target=f"#{REGIAO}",
                hx_swap="outerHTML",
            )
            if editando
            else None,
            cls="filtros-acoes",
        ),
        hx_include=f"#{FILTROS}",
        hx_indicator=f"#{CARREGANDO}",
        hx_post=destino,
        hx_target=f"#{REGIAO}",
        hx_swap="outerHTML",
        method="post",
        action=destino,
        cls="formulario",
    )


def _filtros(
    nome: str = "",
    categoria_id: str = "",
    fornecedor_id: str = "",
    opcoes_categorias: list[tuple[str, str]] | None = None,
    opcoes_fornecedores: list[tuple[str, str]] | None = None,
) -> Form:
    """Filtros da lista: trecho do nome, categoria e fornecedor."""
    return Form(
        campo("Buscar por nome", "filtro_nome", valor=nome, tipo="search"),
        select_campo(
            "Categoria",
            "filtro_categoria_id",
            opcoes_categorias or [],
            valor=categoria_id,
            vazio="Todas",
            vazio_desabilitado=False,
        ),
        select_campo(
            "Fornecedor",
            "filtro_fornecedor_id",
            opcoes_fornecedores or [],
            valor=fornecedor_id,
            vazio="Todos",
            vazio_desabilitado=False,
        ),
        Div(
            botao("Filtrar", "secundario", type="submit"),
            botao(
                "Limpar",
                "ghost",
                type="button",
                hx_get="/produtos/lista",
                hx_target="#cartao-lista-produtos",
                hx_swap="outerHTML",
            ),
            cls="filtros-acoes",
        ),
        id=FILTROS,
        cls="filtros",
        hx_get="/produtos/lista",
        hx_indicator=f"#{CARREGANDO}",
        hx_target="#cartao-lista-produtos",
        hx_swap="outerHTML",
        method="get",
        action="/produtos/lista",
    )


def _lista(
    produtos: list[dict[str, Any]],
    limite: int,
    pode_escrever: bool,
    tem_filtro: bool,
    opcoes_categorias: list[tuple[str, str]],
    opcoes_fornecedores: list[tuple[str, str]],
):
    """Itens da lista, com o saldo sempre visível e ações só para admin."""
    if not produtos:
        mensagem = (
            "Nenhum produto encontrado para a busca" if tem_filtro else "Nenhum produto cadastrado"
        )
        return estado_vazio(mensagem)

    itens = []
    for produto in produtos:
        critico = produto["quantidade_em_estoque"] <= produto["quantidade_minima"]
        itens.append(
            Div(
                Div(
                    Span(produto["nome"], cls="item-titulo"),
                    Span(f"SKU {produto['sku']}", cls="item-meta mono"),
                    cls="item-principal",
                ),
                Span(
                    f"Categoria: {nome_por_id(opcoes_categorias, produto['categoria_id'])}",
                    cls="item-meta",
                ),
                Span(
                    f"Fornecedor: {nome_por_id(opcoes_fornecedores, produto['fornecedor_id'])}",
                    cls="item-meta",
                ),
                Span(f"Estoque: {produto['quantidade_em_estoque']}", cls="item-saldo"),
                Span(f"Mínimo: {produto['quantidade_minima']}", cls="item-meta mono"),
                selo("critico", "Crítico") if critico else None,
                Div(
                    botao(
                        "Editar",
                        "secundario",
                        hx_get=f"/produtos/{produto['id']}/editar",
                        hx_include=f"#{FILTROS}",
                        hx_target=f"#{REGIAO}",
                        hx_swap="outerHTML",
                    ),
                    botao(
                        "Excluir",
                        "danger",
                        hx_post=f"/produtos/{produto['id']}/excluir",
                        hx_include=f"#{FILTROS}",
                        hx_confirm=f"Excluir o produto {produto['nome']}?",
                        hx_target=f"#{REGIAO}",
                        hx_swap="outerHTML",
                    ),
                    cls="acoes",
                )
                if pode_escrever
                else None,
                cls="item",
            )
        )
    return Div(
        Div(*itens, cls="lista"), indicador(CARREGANDO), _carregar_mais(limite, len(produtos))
    )


def _carregar_mais(limite: int, quantidade: int):
    """Botão que amplia a lista mantendo os filtros ativos."""
    if quantidade < limite or limite >= LIMITE_MAXIMO:
        return None
    return botao(
        "Carregar mais",
        "secundario",
        hx_get="/produtos/lista",
        hx_include=f"#{FILTROS}",
        hx_indicator=f"#{CARREGANDO}",
        hx_vals=f'{{"limite": {min(limite + LIMITE_PADRAO, LIMITE_MAXIMO)}}}',
        hx_target="#cartao-lista-produtos",
        hx_swap="outerHTML",
    )


def _buscar(
    sess,
    limite: int,
    filtro_nome: str,
    filtro_categoria_id: str,
    filtro_fornecedor_id: str,
):
    """Devolve `(produtos, erro)`, onde erro é Redirect ou alerta renderizável."""
    params: dict[str, Any] = {"limit": limite, "offset": 0}
    if filtro_nome:
        params["nome"] = filtro_nome
    if filtro_categoria_id:
        params["categoria_id"] = filtro_categoria_id
    if filtro_fornecedor_id:
        params["fornecedor_id"] = filtro_fornecedor_id

    status, corpo = api.listar_produtos(sessao.token_da_sessao(sess), **params)
    if status == 401:
        return None, redirecionar_ao_login(sess)
    if status != 200:
        return None, alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo)))
    return corpo, None


def _contexto(
    sess, limite: int, filtro_nome: str, filtro_categoria_id: str, filtro_fornecedor_id: str
):
    """Busca a lista e as opções dos selects; devolve tudo pronto para render."""
    produtos, erro = _buscar(sess, limite, filtro_nome, filtro_categoria_id, filtro_fornecedor_id)
    if isinstance(erro, Redirect):
        return None, erro, None, None
    return (
        produtos,
        erro,
        opcoes_categorias(sess),
        opcoes_fornecedores(sess),
    )


def _cartao_lista(
    sess,
    limite: int,
    filtro_nome: str = "",
    filtro_categoria_id: str = "",
    filtro_fornecedor_id: str = "",
):
    """Cartão da lista (ou do erro) — alvo dos filtros e do "carregar mais"."""
    produtos, erro = _buscar(sess, limite, filtro_nome, filtro_categoria_id, filtro_fornecedor_id)
    if isinstance(erro, Redirect):
        return erro
    catalogo_categorias = opcoes_categorias(sess)
    catalogo_fornecedores = opcoes_fornecedores(sess)
    return cartao(
        _filtros(
            filtro_nome,
            filtro_categoria_id,
            filtro_fornecedor_id,
            catalogo_categorias,
            catalogo_fornecedores,
        ),
        erro
        if erro is not None
        else _lista(
            produtos,
            limite,
            sessao.eh_admin(sess),
            bool(filtro_nome or filtro_categoria_id or filtro_fornecedor_id),
            catalogo_categorias,
            catalogo_fornecedores,
        ),
        indicador(CARREGANDO),
        titulo="Produtos cadastrados",
        id_="cartao-lista-produtos",
    )


def _regiao(
    sess,
    *,
    alerta_=None,
    form: Any | None = None,
    titulo_form: str = "Novo produto",
    limite: int = LIMITE_PADRAO,
    filtro_nome: str = "",
    filtro_categoria_id: str = "",
    filtro_fornecedor_id: str = "",
):
    """Região mutável da tela: aviso + formulário + lista filtrada."""
    produtos, erro, catalogo_categorias, catalogo_fornecedores = _contexto(
        sess, limite, filtro_nome, filtro_categoria_id, filtro_fornecedor_id
    )
    if isinstance(erro, Redirect):
        return erro

    return Div(
        alerta_,
        cartao(
            form
            if form is not None
            else _form(
                opcoes_categorias=catalogo_categorias,
                opcoes_fornecedores=catalogo_fornecedores,
            ),
            titulo=titulo_form,
            id_="cartao-form-produto",
        )
        if sessao.eh_admin(sess)
        else None,
        cartao(
            _filtros(
                filtro_nome,
                filtro_categoria_id,
                filtro_fornecedor_id,
                catalogo_categorias,
                catalogo_fornecedores,
            ),
            erro
            if erro is not None
            else _lista(
                produtos,
                limite,
                sessao.eh_admin(sess),
                bool(filtro_nome or filtro_categoria_id or filtro_fornecedor_id),
                catalogo_categorias,
                catalogo_fornecedores,
            ),
            indicador(CARREGANDO),
            titulo="Produtos cadastrados",
            id_="cartao-lista-produtos",
        ),
        id=REGIAO,
    )


@ar("/produtos", methods=["GET"])
def tela_produtos(sess):
    """Página completa: filtros, formulário e lista paginada."""
    regiao = _regiao(sess)
    if isinstance(regiao, Redirect):
        return regiao
    return shell(H1("Produtos"), regiao, sess=sess, atual="/produtos", nome_pagina="Produtos")


@ar("/produtos/novo", methods=["GET"])
def novo_produto(sess):
    """Devolve a região no modo de criação (botão Cancelar da edição)."""
    return _regiao(sess)


@ar("/produtos/lista", methods=["GET"])
def lista_produtos(
    sess,
    filtro_nome: str = "",
    filtro_categoria_id: str = "",
    filtro_fornecedor_id: str = "",
    limite: int = LIMITE_PADRAO,
):
    """Cartão da lista filtrada — alvo dos filtros e do "carregar mais"."""
    limite = max(LIMITE_PADRAO, min(int(limite), LIMITE_MAXIMO))
    return _cartao_lista(
        sess,
        limite,
        filtro_nome.strip(),
        filtro_categoria_id.strip(),
        filtro_fornecedor_id.strip(),
    )


@ar("/produtos/{produto_id}/editar", methods=["GET"])
def editar_produto(
    sess,
    produto_id: int,
    filtro_nome: str = "",
    filtro_categoria_id: str = "",
    filtro_fornecedor_id: str = "",
):
    """Região com o formulário preenchido para edição."""
    status, corpo = api.obter_produto(sessao.token_da_sessao(sess), produto_id)
    if status == 401:
        return redirecionar_ao_login(sess)
    if status != 200:
        return _regiao(
            sess,
            alerta_=alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo))),
            filtro_nome=filtro_nome.strip(),
            filtro_categoria_id=filtro_categoria_id.strip(),
            filtro_fornecedor_id=filtro_fornecedor_id.strip(),
        )
    return _regiao(
        sess,
        form=_form(
            nome=corpo["nome"],
            sku=corpo["sku"],
            preco_custo=corpo["preco_custo"],
            preco_venda=corpo["preco_venda"],
            quantidade_minima=corpo["quantidade_minima"],
            categoria_id=corpo["categoria_id"],
            fornecedor_id=corpo["fornecedor_id"],
            produto_id=corpo["id"],
            opcoes_categorias=opcoes_categorias(sess),
            opcoes_fornecedores=opcoes_fornecedores(sess),
        ),
        titulo_form="Editar produto",
        filtro_nome=filtro_nome.strip(),
        filtro_categoria_id=filtro_categoria_id.strip(),
        filtro_fornecedor_id=filtro_fornecedor_id.strip(),
    )


def _dados_formulario(
    nome: str,
    sku: str,
    preco_custo: str,
    preco_venda: str,
    quantidade_minima: Any,
    categoria_id: Any,
    fornecedor_id: Any,
) -> dict[str, Any]:
    """Converte os campos do formulário no payload da API."""
    return {
        "nome": nome.strip(),
        "sku": sku.strip(),
        "preco_custo": preco_custo.strip(),
        "preco_venda": preco_venda.strip(),
        "quantidade_minima": _inteiro(quantidade_minima),
        "categoria_id": _inteiro(categoria_id),
        "fornecedor_id": _inteiro(fornecedor_id),
    }


def _criar_ou_atualizar(
    sess,
    *,
    produto_id: int | None,
    dados: dict[str, Any],
    status_ok: int,
    aviso: str,
    filtros: dict[str, str],
):
    """Corpo comum de criação e edição: chama a API e devolve a região."""
    token = sessao.token_da_sessao(sess)
    if produto_id is None:
        status, corpo = api.criar_produto(token, dados)
    else:
        status, corpo = api.atualizar_produto(token, produto_id, dados)

    if status == 401:
        return redirecionar_ao_login(sess)
    if status == status_ok:
        return _regiao(sess, alerta_=alerta("sucesso", aviso), **filtros)
    if status == 422:
        return _regiao(
            sess,
            alerta_=alerta("erro", "Há campos inválidos."),
            form=_form(
                **dados,
                produto_id=produto_id,
                erros=api.erros_por_campo(api.detail_do_corpo(corpo)),
                opcoes_categorias=opcoes_categorias(sess),
                opcoes_fornecedores=opcoes_fornecedores(sess),
            ),
            titulo_form="Editar produto" if produto_id else "Novo produto",
            **filtros,
        )
    return _regiao(
        sess,
        alerta_=alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo))),
        form=_form(
            **dados,
            produto_id=produto_id,
            opcoes_categorias=opcoes_categorias(sess),
            opcoes_fornecedores=opcoes_fornecedores(sess),
        ),
        titulo_form="Editar produto" if produto_id else "Novo produto",
        **filtros,
    )


def _escrita_recusada(sess, filtros: dict[str, str]):
    """403 com a região quando o leitor força uma rota de escrita."""
    regiao = _regiao(sess, alerta_=alerta("erro", SEM_PERMISSAO), **filtros)
    if isinstance(regiao, Redirect):
        return regiao
    return resposta_403(regiao)


@ar("/produtos", methods=["POST"])
def criar_produto(
    sess,
    nome: str = "",
    sku: str = "",
    preco_custo: str = "",
    preco_venda: str = "",
    quantidade_minima: str = "0",
    categoria_id: str = "",
    fornecedor_id: str = "",
    filtro_nome: str = "",
    filtro_categoria_id: str = "",
    filtro_fornecedor_id: str = "",
):
    """Cria o produto; SKU repetido volta como 409 da API."""
    if not sessao.eh_admin(sess):
        return _escrita_recusada(
            sess,
            {
                "filtro_nome": filtro_nome,
                "filtro_categoria_id": filtro_categoria_id,
                "filtro_fornecedor_id": filtro_fornecedor_id,
            },
        )
    return _criar_ou_atualizar(
        sess,
        produto_id=None,
        dados=_dados_formulario(
            nome, sku, preco_custo, preco_venda, quantidade_minima, categoria_id, fornecedor_id
        ),
        status_ok=201,
        aviso="Produto criado.",
        filtros={
            "filtro_nome": filtro_nome.strip(),
            "filtro_categoria_id": filtro_categoria_id.strip(),
            "filtro_fornecedor_id": filtro_fornecedor_id.strip(),
        },
    )


@ar("/produtos/{produto_id}", methods=["POST"])
def atualizar_produto(
    sess,
    produto_id: int,
    nome: str = "",
    sku: str = "",
    preco_custo: str = "",
    preco_venda: str = "",
    quantidade_minima: str = "0",
    categoria_id: str = "",
    fornecedor_id: str = "",
    filtro_nome: str = "",
    filtro_categoria_id: str = "",
    filtro_fornecedor_id: str = "",
):
    """Atualiza o produto; o saldo não entra no payload (só movimentação)."""
    if not sessao.eh_admin(sess):
        return _escrita_recusada(
            sess,
            {
                "filtro_nome": filtro_nome,
                "filtro_categoria_id": filtro_categoria_id,
                "filtro_fornecedor_id": filtro_fornecedor_id,
            },
        )
    return _criar_ou_atualizar(
        sess,
        produto_id=produto_id,
        dados=_dados_formulario(
            nome, sku, preco_custo, preco_venda, quantidade_minima, categoria_id, fornecedor_id
        ),
        status_ok=200,
        aviso="Produto atualizado.",
        filtros={
            "filtro_nome": filtro_nome.strip(),
            "filtro_categoria_id": filtro_categoria_id.strip(),
            "filtro_fornecedor_id": filtro_fornecedor_id.strip(),
        },
    )


@ar("/produtos/{produto_id}/excluir", methods=["POST"])
def excluir_produto(
    sess,
    produto_id: int,
    filtro_nome: str = "",
    filtro_categoria_id: str = "",
    filtro_fornecedor_id: str = "",
):
    """Exclui o produto; com movimentações registradas a API responde 409."""
    filtros = {
        "filtro_nome": filtro_nome.strip(),
        "filtro_categoria_id": filtro_categoria_id.strip(),
        "filtro_fornecedor_id": filtro_fornecedor_id.strip(),
    }
    if not sessao.eh_admin(sess):
        return _escrita_recusada(sess, filtros)

    status, corpo = api.excluir_produto(sessao.token_da_sessao(sess), produto_id)
    if status == 401:
        return redirecionar_ao_login(sess)
    if status == 204:
        return _regiao(sess, alerta_=alerta("sucesso", "Produto excluído."), **filtros)
    return _regiao(
        sess,
        alerta_=alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo))),
        **filtros,
    )
