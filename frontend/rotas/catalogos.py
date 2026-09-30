"""Catálogos de apoio do painel: categorias e fornecedores como opções/nomes.

Os selects de filtros e formulários e a tradução id → nome dos itens usam estes
helpers; a API é sempre a fonte (nenhuma consulta direta ao banco no painel).
"""

from typing import Any

from frontend import api, sessao

LIMITE_OPCOES = 100


def opcoes_categorias(sess) -> list[tuple[str, str]]:
    """Categorias no formato `(id, nome)` para selects."""
    status, corpo = api.listar_categorias(
        sessao.token_da_sessao(sess), limit=LIMITE_OPCOES, offset=0
    )
    if status != 200:
        return []
    return [(str(item["id"]), item["nome"]) for item in corpo]


def opcoes_fornecedores(sess) -> list[tuple[str, str]]:
    """Fornecedores no formato `(id, nome)` para selects."""
    status, corpo = api.listar_fornecedores(
        sessao.token_da_sessao(sess), limit=LIMITE_OPCOES, offset=0
    )
    if status != 200:
        return []
    return [(str(item["id"]), item["nome"]) for item in corpo]


def opcoes_produtos(sess) -> list[tuple[str, str]]:
    """Produtos no formato `(id, nome)` para selects e mapas de nome."""
    status, corpo = api.listar_produtos(
        sessao.token_da_sessao(sess), limit=LIMITE_OPCOES, offset=0
    )
    if status != 200:
        return []
    return [(str(item["id"]), item["nome"]) for item in corpo]


def nome_por_id(opcoes: list[tuple[str, str]], identificador: Any, prefixo: str = "#") -> str:
    """Resolve o nome a partir das opções; `#id` quando a lista não alcança."""
    for valor, nome in opcoes:
        if valor == str(identificador):
            return nome
    return f"{prefixo}{identificador}"
