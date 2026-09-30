"""Tela de fornecedores — lista com filtro por nome e CRUD completo."""

from typing import Any

from fasthtml.common import APIRouter, Div, Form, Input, Redirect, Span

from frontend import api, sessao
from frontend.componentes import alerta, botao, campo, cartao, estado_vazio, shell
from frontend.rotas import SEM_PERMISSAO, redirecionar_ao_login, resposta_403

ar = APIRouter()

REGIAO = "conteudo-fornecedores"
FILTROS = "filtros-fornecedores"
LIMITE_PADRAO = 20
LIMITE_MAXIMO = 100


def _form(
    *,
    nome: str = "",
    cnpj: str = "",
    telefone: str = "",
    email: str = "",
    fornecedor_id: int | None = None,
    erros: dict[str, str] | None = None,
) -> Form:
    """Formulário de criar/editar fornecedor — o mesmo componente nos dois modos."""
    erros = erros or {}
    editando = fornecedor_id is not None
    destino = f"/fornecedores/{fornecedor_id}" if editando else "/fornecedores"
    return Form(
        Input(type="hidden", name="fornecedor_id", value=fornecedor_id) if editando else None,
        campo("Nome", "nome", valor=nome, erro=erros.get("nome"), required=True, maxlength=120),
        campo(
            "CNPJ",
            "cnpj",
            valor=cnpj,
            erro=erros.get("cnpj"),
            required=True,
            placeholder="00.000.000/0000-00",
        ),
        campo(
            "Telefone",
            "telefone",
            tipo="tel",
            valor=telefone,
            erro=erros.get("telefone"),
            required=True,
            maxlength=20,
        ),
        campo("E-mail", "email", tipo="email", valor=email, erro=erros.get("email"), required=True),
        Div(
            botao("Salvar", "primario", type="submit"),
            botao(
                "Cancelar",
                "ghost",
                type="button",
                hx_get="/fornecedores/novo",
                hx_target=f"#{REGIAO}",
                hx_swap="outerHTML",
            )
            if editando
            else None,
            cls="filtros-acoes",
        ),
        # o filtro ativo viaja junto para a lista não perder o recorte
        hx_include=f"#{FILTROS}",
        hx_post=destino,
        hx_target=f"#{REGIAO}",
        hx_swap="outerHTML",
        method="post",
        action=destino,
    )


def _filtros(nome: str = "") -> Form:
    """Formulário de busca por trecho do nome (filtro da API)."""
    return Form(
        campo("Buscar por nome", "filtro_nome", valor=nome, tipo="search"),
        Div(
            botao("Filtrar", "secundario", type="submit"),
            botao(
                "Limpar",
                "ghost",
                type="button",
                hx_get="/fornecedores/lista",
                hx_target="#cartao-lista-fornecedores",
                hx_swap="outerHTML",
            ),
            cls="filtros-acoes",
        ),
        id=FILTROS,
        cls="filtros",
        hx_get="/fornecedores/lista",
        hx_target="#cartao-lista-fornecedores",
        hx_swap="outerHTML",
        method="get",
        action="/fornecedores/lista",
    )


def _lista(fornecedores: list[dict[str, Any]], limite: int, pode_escrever: bool, filtro: str):
    """Itens da lista; ações de escrita não existem para leitor."""
    if not fornecedores:
        mensagem = (
            "Nenhum fornecedor encontrado para a busca"
            if filtro
            else "Nenhum fornecedor cadastrado"
        )
        return estado_vazio(mensagem)

    itens = [
        Div(
            Div(Span(fornecedor["nome"], cls="item-titulo"), cls="item-principal"),
            Span(f"CNPJ {fornecedor['cnpj']}", cls="item-meta mono"),
            Span(fornecedor["telefone"], cls="item-meta mono"),
            Span(fornecedor["email"], cls="item-meta"),
            Div(
                botao(
                    "Editar",
                    "secundario",
                    hx_get=f"/fornecedores/{fornecedor['id']}/editar",
                    hx_include=f"#{FILTROS}",
                    hx_target=f"#{REGIAO}",
                    hx_swap="outerHTML",
                ),
                botao(
                    "Excluir",
                    "danger",
                    hx_post=f"/fornecedores/{fornecedor['id']}/excluir",
                    hx_include=f"#{FILTROS}",
                    hx_confirm=f"Excluir o fornecedor {fornecedor['nome']}?",
                    hx_target=f"#{REGIAO}",
                    hx_swap="outerHTML",
                ),
                cls="acoes",
            )
            if pode_escrever
            else None,
            cls="item",
        )
        for fornecedor in fornecedores
    ]
    return Div(Div(*itens, cls="lista"), _carregar_mais(limite, len(fornecedores)))


def _carregar_mais(limite: int, quantidade: int):
    """Botão que amplia a lista mantendo o filtro ativo."""
    if quantidade < limite or limite >= LIMITE_MAXIMO:
        return None
    return botao(
        "Carregar mais",
        "secundario",
        hx_get="/fornecedores/lista",
        hx_include=f"#{FILTROS}",
        hx_vals=f'{{"limite": {min(limite + LIMITE_PADRAO, LIMITE_MAXIMO)}}}',
        hx_target="#cartao-lista-fornecedores",
        hx_swap="outerHTML",
    )


def _buscar(sess, limite: int, filtro: str):
    """Devolve `(fornecedores, erro)`, onde erro é Redirect ou alerta renderizável."""
    params: dict[str, Any] = {"limit": limite, "offset": 0}
    if filtro:
        params["nome"] = filtro
    status, corpo = api.listar_fornecedores(sessao.token_da_sessao(sess), **params)
    if status == 401:
        return None, redirecionar_ao_login(sess)
    if status != 200:
        return None, alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo)))
    return corpo, None


def _cartao_lista(sess, limite: int, filtro: str, erro=None):
    """Cartão da lista (ou do erro) — alvo dos filtros e do "carregar mais"."""
    if erro is None:
        fornecedores, erro = _buscar(sess, limite, filtro)
        if isinstance(erro, Redirect):
            return erro
    return cartao(
        _filtros(filtro),
        erro if erro is not None else _lista(fornecedores, limite, sessao.eh_admin(sess), filtro),
        titulo="Fornecedores cadastrados",
        id_="cartao-lista-fornecedores",
    )


def _regiao(
    sess,
    *,
    alerta_=None,
    form: Any | None = None,
    titulo_form: str = "Novo fornecedor",
    limite: int = LIMITE_PADRAO,
    filtro: str = "",
):
    """Região mutável da tela: aviso + formulário + lista filtrada."""
    fornecedores, erro = _buscar(sess, limite, filtro)
    if isinstance(erro, Redirect):
        return erro

    return Div(
        alerta_,
        cartao(
            form if form is not None else _form(),
            titulo=titulo_form,
            id_="cartao-form-fornecedor",
        )
        if sessao.eh_admin(sess)
        else None,
        cartao(
            _filtros(filtro),
            erro
            if erro is not None
            else _lista(fornecedores, limite, sessao.eh_admin(sess), filtro),
            titulo="Fornecedores cadastrados",
            id_="cartao-lista-fornecedores",
        ),
        id=REGIAO,
    )


@ar("/fornecedores", methods=["GET"])
def tela_fornecedores(sess):
    """Página completa: filtro, formulário e lista paginada."""
    regiao = _regiao(sess)
    if isinstance(regiao, Redirect):
        return regiao
    return shell(regiao, sess=sess, atual="/fornecedores", nome_pagina="Fornecedores")


@ar("/fornecedores/novo", methods=["GET"])
def novo_fornecedor(sess):
    """Devolve a região no modo de criação (botão Cancelar da edição)."""
    return _regiao(sess)


@ar("/fornecedores/lista", methods=["GET"])
def lista_fornecedores(sess, filtro_nome: str = "", limite: int = LIMITE_PADRAO):
    """Cartão da lista filtrada — alvo do filtro e do "carregar mais"."""
    limite = max(LIMITE_PADRAO, min(int(limite), LIMITE_MAXIMO))
    return _cartao_lista(sess, limite, filtro_nome.strip())


@ar("/fornecedores/{fornecedor_id}/editar", methods=["GET"])
def editar_fornecedor(sess, fornecedor_id: int, filtro_nome: str = ""):
    """Região com o formulário preenchido para edição."""
    status, corpo = api.obter_fornecedor(sessao.token_da_sessao(sess), fornecedor_id)
    if status == 401:
        return redirecionar_ao_login(sess)
    if status != 200:
        return _regiao(
            sess,
            alerta_=alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo))),
            filtro=filtro_nome.strip(),
        )
    return _regiao(
        sess,
        form=_form(
            nome=corpo["nome"],
            cnpj=corpo["cnpj"],
            telefone=corpo["telefone"],
            email=corpo["email"],
            fornecedor_id=corpo["id"],
        ),
        titulo_form="Editar fornecedor",
        filtro=filtro_nome.strip(),
    )


def _criar_ou_atualizar(
    sess,
    *,
    fornecedor_id: int | None,
    dados: dict[str, str],
    status_ok: int,
    aviso: str,
    filtro: str,
):
    """Corpo comum de criação e edição: chama a API e devolve a região."""
    token = sessao.token_da_sessao(sess)
    if fornecedor_id is None:
        status, corpo = api.criar_fornecedor(token, dados)
    else:
        status, corpo = api.atualizar_fornecedor(token, fornecedor_id, dados)

    if status == 401:
        return redirecionar_ao_login(sess)
    if status == status_ok:
        return _regiao(sess, alerta_=alerta("sucesso", aviso), filtro=filtro)
    if status == 422:
        return _regiao(
            sess,
            alerta_=alerta("erro", "Há campos inválidos."),
            form=_form(
                **dados,
                fornecedor_id=fornecedor_id,
                erros=api.erros_por_campo(api.detail_do_corpo(corpo)),
            ),
            titulo_form="Editar fornecedor" if fornecedor_id else "Novo fornecedor",
            filtro=filtro,
        )
    return _regiao(
        sess,
        alerta_=alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo))),
        form=_form(**dados, fornecedor_id=fornecedor_id),
        titulo_form="Editar fornecedor" if fornecedor_id else "Novo fornecedor",
        filtro=filtro,
    )


def _escrita_recusada(sess, filtro: str):
    """403 com a região quando o leitor força uma rota de escrita."""
    regiao = _regiao(sess, alerta_=alerta("erro", SEM_PERMISSAO), filtro=filtro)
    if isinstance(regiao, Redirect):
        return regiao
    return resposta_403(regiao)


@ar("/fornecedores", methods=["POST"])
def criar_fornecedor(
    sess,
    nome: str = "",
    cnpj: str = "",
    telefone: str = "",
    email: str = "",
    filtro_nome: str = "",
):
    """Cria o fornecedor; CNPJ/e-mail repetidos voltam como 409 da API."""
    if not sessao.eh_admin(sess):
        return _escrita_recusada(sess, filtro_nome.strip())
    return _criar_ou_atualizar(
        sess,
        fornecedor_id=None,
        dados={"nome": nome, "cnpj": cnpj, "telefone": telefone, "email": email},
        status_ok=201,
        aviso="Fornecedor criado.",
        filtro=filtro_nome.strip(),
    )


@ar("/fornecedores/{fornecedor_id}", methods=["POST"])
def atualizar_fornecedor(
    sess,
    fornecedor_id: int,
    nome: str = "",
    cnpj: str = "",
    telefone: str = "",
    email: str = "",
    filtro_nome: str = "",
):
    """Atualiza o fornecedor; unicidade de CNPJ/e-mail continua valendo."""
    if not sessao.eh_admin(sess):
        return _escrita_recusada(sess, filtro_nome.strip())
    return _criar_ou_atualizar(
        sess,
        fornecedor_id=fornecedor_id,
        dados={"nome": nome, "cnpj": cnpj, "telefone": telefone, "email": email},
        status_ok=200,
        aviso="Fornecedor atualizado.",
        filtro=filtro_nome.strip(),
    )


@ar("/fornecedores/{fornecedor_id}/excluir", methods=["POST"])
def excluir_fornecedor(sess, fornecedor_id: int, filtro_nome: str = ""):
    """Exclui o fornecedor; vínculo com produto volta como 409 da API."""
    if not sessao.eh_admin(sess):
        return _escrita_recusada(sess, filtro_nome.strip())

    status, corpo = api.excluir_fornecedor(sessao.token_da_sessao(sess), fornecedor_id)
    if status == 401:
        return redirecionar_ao_login(sess)
    if status == 204:
        return _regiao(
            sess, alerta_=alerta("sucesso", "Fornecedor excluído."), filtro=filtro_nome.strip()
        )
    return _regiao(
        sess,
        alerta_=alerta("erro", api.mensagem_do_detail(api.detail_do_corpo(corpo))),
        filtro=filtro_nome.strip(),
    )
