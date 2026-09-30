"""Tela de categorias — lista e CRUD; exclusão com produtos vinculados dá 409."""

from typing import Any

from fasthtml.common import H1, APIRouter, Div, Form, Input, Redirect, Span

from frontend import api, sessao
from frontend.componentes import (
    alerta,
    botao,
    campo,
    cartao,
    estado_vazio,
    shell,
)
from frontend.rotas import SEM_PERMISSAO, redirecionar_ao_login, resposta_403

ar = APIRouter()

REGIAO = "conteudo-categorias"
LIMITE_PADRAO = 20
LIMITE_MAXIMO = 100


def _form(
    nome: str = "",
    categoria_id: int | None = None,
    erros: dict[str, str] | None = None,
) -> Form:
    """Formulário de criar/editar categoria — o mesmo componente nos dois modos."""
    editando = categoria_id is not None
    destino = f"/categorias/{categoria_id}" if editando else "/categorias"
    return Form(
        Input(type="hidden", name="categoria_id", value=categoria_id) if editando else None,
        campo(
            "Nome",
            "nome",
            valor=nome,
            erro=(erros or {}).get("nome"),
            required=True,
            maxlength=120,
        ),
        Div(
            botao("Salvar", "primario", type="submit"),
            botao(
                "Cancelar",
                "ghost",
                type="button",
                hx_get="/categorias/novo",
                hx_target=f"#{REGIAO}",
                hx_swap="outerHTML",
            )
            if editando
            else None,
            cls="filtros-acoes",
        ),
        hx_post=destino,
        hx_target=f"#{REGIAO}",
        hx_swap="outerHTML",
        method="post",
        action=destino,
    )


def _lista(categorias: list[dict[str, Any]], limite: int, pode_escrever: bool):
    """Itens da lista; o botão "carregar mais" só aparece se há próxima faixa.

    Para leitor, as ações de escrita não existem (não são desabilitadas).
    """
    if not categorias:
        return estado_vazio("Nenhuma categoria cadastrada")

    itens = [
        Div(
            Div(Span(categoria["nome"], cls="item-titulo"), cls="item-principal"),
            Div(
                botao(
                    "Editar",
                    "secundario",
                    hx_get=f"/categorias/{categoria['id']}/editar",
                    hx_target=f"#{REGIAO}",
                    hx_swap="outerHTML",
                ),
                botao(
                    "Excluir",
                    "danger",
                    hx_post=f"/categorias/{categoria['id']}/excluir",
                    hx_confirm=f"Excluir a categoria {categoria['nome']}?",
                    hx_target=f"#{REGIAO}",
                    hx_swap="outerHTML",
                ),
                cls="acoes",
            )
            if pode_escrever
            else None,
            cls="item",
        )
        for categoria in categorias
    ]
    return Div(Div(*itens, cls="lista"), _carregar_mais(limite, len(categorias)))


def _carregar_mais(limite: int, quantidade: int):
    """Botão que refaz a lista com mais itens (limit/offset da API)."""
    if quantidade < limite or limite >= LIMITE_MAXIMO:
        return None
    return botao(
        "Carregar mais",
        "secundario",
        hx_get="/categorias/lista",
        hx_vals=f'{{"limite": {min(limite + LIMITE_PADRAO, LIMITE_MAXIMO)}}}',
        hx_target="#cartao-lista-categorias",
        hx_swap="outerHTML",
    )


def _buscar(sess, limite: int):
    """Devolve `(categorias, erro)`, onde erro é Redirect ou alerta renderizável."""
    status, corpo = api.listar_categorias(sessao.token_da_sessao(sess), limit=limite, offset=0)
    if status == 401:
        return None, redirecionar_ao_login(sess)
    if status != 200:
        return None, alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo)))
    return corpo, None


def _cartao_lista(sess, limite: int, erro=None):
    """Cartão da lista (ou do erro) — o alvo de filtros e do "carregar mais"."""
    if erro is None:
        categorias, erro = _buscar(sess, limite)
        if isinstance(erro, Redirect):
            return erro
    return cartao(
        erro if erro is not None else _lista(categorias, limite, sessao.eh_admin(sess)),
        titulo="Categorias cadastradas",
        id_="cartao-lista-categorias",
    )


def _regiao(
    sess,
    *,
    alerta_=None,
    form: Any | None = None,
    titulo_form: str = "Nova categoria",
    limite: int = LIMITE_PADRAO,
):
    """Região mutável da tela: aviso + formulário + lista."""
    categorias, erro = _buscar(sess, limite)
    if isinstance(erro, Redirect):
        return erro

    return Div(
        alerta_,
        cartao(
            form if form is not None else _form(),
            titulo=titulo_form,
            id_="cartao-form-categoria",
        )
        if sessao.eh_admin(sess)
        else None,
        cartao(
            erro if erro is not None else _lista(categorias, limite, sessao.eh_admin(sess)),
            titulo="Categorias cadastradas",
            id_="cartao-lista-categorias",
        ),
        id=REGIAO,
    )


@ar("/categorias", methods=["GET"])
def tela_categorias(sess):
    """Página completa: formulário de criação e lista paginada."""
    regiao = _regiao(sess)
    if isinstance(regiao, Redirect):
        return regiao
    return shell(H1("Categorias"), regiao, sess=sess, atual="/categorias", nome_pagina="Categorias")


@ar("/categorias/novo", methods=["GET"])
def novo_categoria(sess):
    """Devolve a região no modo de criação (botão Cancelar da edição)."""
    return _regiao(sess)


@ar("/categorias/lista", methods=["GET"])
def lista_categorias(sess, limite: int = LIMITE_PADRAO):
    """Cartão da lista com mais itens — alvo do "carregar mais"."""
    limite = max(LIMITE_PADRAO, min(int(limite), LIMITE_MAXIMO))
    return _cartao_lista(sess, limite)


@ar("/categorias/{categoria_id}/editar", methods=["GET"])
def editar_categoria(sess, categoria_id: int):
    """Região com o formulário preenchido para edição."""
    status, corpo = api.obter_categoria(sessao.token_da_sessao(sess), categoria_id)
    if status == 401:
        return redirecionar_ao_login(sess)
    if status != 200:
        return _regiao(
            sess, alerta_=alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo)))
        )
    return _regiao(
        sess,
        form=_form(nome=corpo["nome"], categoria_id=corpo["id"]),
        titulo_form="Editar categoria",
    )


def _criar_ou_atualizar(sess, *, categoria_id: int | None, nome: str, status_ok: int, aviso: str):
    """Corpo comum de criação e edição: chama a API e devolve a região."""
    token = sessao.token_da_sessao(sess)
    if categoria_id is None:
        status, corpo = api.criar_categoria(token, {"nome": nome})
    else:
        status, corpo = api.atualizar_categoria(token, categoria_id, {"nome": nome})

    if status == 401:
        return redirecionar_ao_login(sess)
    if status == status_ok:
        return _regiao(sess, alerta_=alerta("sucesso", aviso))
    if status == 422:
        return _regiao(
            sess,
            alerta_=alerta("erro", "Há campos inválidos."),
            form=_form(
                nome=nome,
                categoria_id=categoria_id,
                erros=api.erros_por_campo(api.detail_do_corpo(corpo)),
            ),
        )
    return _regiao(
        sess,
        alerta_=alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo))),
        form=_form(nome=nome, categoria_id=categoria_id),
    )


def _escrita_recusada(sess):
    """403 com a região quando o leitor força uma rota de escrita."""
    regiao = _regiao(sess, alerta_=alerta("erro", SEM_PERMISSAO))
    if isinstance(regiao, Redirect):
        return regiao
    return resposta_403(regiao)


@ar("/categorias", methods=["POST"])
def criar_categoria(sess, nome: str = ""):
    """Cria a categoria; nome repetido volta como 409 da API."""
    if not sessao.eh_admin(sess):
        return _escrita_recusada(sess)
    return _criar_ou_atualizar(
        sess, categoria_id=None, nome=nome, status_ok=201, aviso="Categoria criada."
    )


@ar("/categorias/{categoria_id}", methods=["POST"])
def atualizar_categoria(sess, categoria_id: int, nome: str = ""):
    """Renomeia a categoria; nome repetido volta como 409 da API."""
    if not sessao.eh_admin(sess):
        return _escrita_recusada(sess)
    return _criar_ou_atualizar(
        sess, categoria_id=categoria_id, nome=nome, status_ok=200, aviso="Categoria atualizada."
    )


@ar("/categorias/{categoria_id}/excluir", methods=["POST"])
def excluir_categoria(sess, categoria_id: int):
    """Exclui a categoria; vínculo com produto volta como 409 da API."""
    if not sessao.eh_admin(sess):
        return _escrita_recusada(sess)

    status, corpo = api.excluir_categoria(sessao.token_da_sessao(sess), categoria_id)
    if status == 401:
        return redirecionar_ao_login(sess)
    if status == 204:
        return _regiao(sess, alerta_=alerta("sucesso", "Categoria excluída."))
    return _regiao(sess, alerta_=alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo))))
