"""Confere que o schema reflete os invariantes do SPEC (ADRs 0001, 0002, 0003, 0005)."""

import pytest
from sqlalchemy import delete, insert, inspect, select, text
from sqlalchemy.exc import IntegrityError

from app.db import engine
from app.models import Base, TipoMovimentacao

TABELAS = Base.metadata.tables


@pytest.fixture()
def conexao():
    """Cria o schema numa transação do Postgres e desfaz ao final.

    O Postgres tem DDL transacional, então cada teste enxerga um banco com as
    tabelas criadas e não deixa resíduo para os demais.
    """
    with engine.connect() as conn:
        transacao = conn.begin()
        Base.metadata.create_all(conn)
        try:
            yield conn
        finally:
            transacao.rollback()


def _cria_fornecedor(conn, **extra):
    valores = {
        "nome": "Fornecedor Um",
        "cnpj": "11222333000181",
        "telefone": "75999990000",
        "email": "fornecedor@exemplo.com",
    }
    valores.update(extra)
    resultado = conn.execute(insert(TABELAS["fornecedores"]).values(**valores))
    return resultado.inserted_primary_key[0]


def _cria_categoria(conn, nome="Bebidas"):
    resultado = conn.execute(insert(TABELAS["categorias"]).values(nome=nome))
    return resultado.inserted_primary_key[0]


def _cria_produto(conn, categoria_id, fornecedor_id, **extra):
    valores = {
        "nome": "Produto Um",
        "sku": "SKU-1",
        "preco_custo": "10.00",
        "preco_venda": "15.00",
        "categoria_id": categoria_id,
        "fornecedor_id": fornecedor_id,
    }
    valores.update(extra)
    resultado = conn.execute(insert(TABELAS["produtos"]).values(**valores))
    return resultado.inserted_primary_key[0]


def _deve_falhar(conn, tabela, **valores):
    with pytest.raises(IntegrityError), conn.begin_nested():
        conn.execute(insert(tabela).values(**valores))


def test_tabelas_e_enum_de_movimentacao(conexao):
    nomes = set(inspect(conexao).get_table_names())
    assert {"fornecedores", "categorias", "produtos", "movimentacoes"} <= nomes

    rotulos = (
        conexao.execute(
            text(
                "SELECT e.enumlabel FROM pg_enum e "
                "JOIN pg_type t ON t.oid = e.enumtypid "
                "WHERE t.typname = 'tipo_movimentacao' "
                "ORDER BY e.enumsortorder"
            )
        )
        .scalars()
        .all()
    )
    assert rotulos == ["entrada", "saida"]


def test_unicidades_de_fornecedor(conexao):
    _cria_fornecedor(conexao)

    _deve_falhar(
        conexao,
        TABELAS["fornecedores"],
        nome="Fornecedor Dois",
        cnpj="11222333000181",
        telefone="1",
        email="outro@exemplo.com",
    )
    # E-mail é único ignorando caixa (índice funcional em lower(email)).
    _deve_falhar(
        conexao,
        TABELAS["fornecedores"],
        nome="Fornecedor Três",
        cnpj="99888777000166",
        telefone="1",
        email="FORNECEDOR@EXEMPLO.COM",
    )


def test_unicidade_de_categoria_ignorando_caixa(conexao):
    _cria_categoria(conexao, "Bebidas")
    _deve_falhar(conexao, TABELAS["categorias"], nome="bebidas")


def test_invariantes_numericos_de_produto(conexao):
    fornecedor_id = _cria_fornecedor(conexao)
    categoria_id = _cria_categoria(conexao)
    _cria_produto(conexao, categoria_id, fornecedor_id)

    base = {
        "nome": "Produto Inválido",
        "preco_custo": "1.00",
        "preco_venda": "2.00",
        "categoria_id": categoria_id,
        "fornecedor_id": fornecedor_id,
    }
    _deve_falhar(conexao, TABELAS["produtos"], sku="SKU-1", **base)
    _deve_falhar(conexao, TABELAS["produtos"], sku="SKU-2", quantidade_em_estoque=-1, **base)
    _deve_falhar(conexao, TABELAS["produtos"], sku="SKU-3", quantidade_minima=-1, **base)
    _deve_falhar(conexao, TABELAS["produtos"], **(base | {"sku": "SKU-4", "preco_custo": "-1.00"}))


def test_produto_nasce_com_saldo_zero(conexao):
    fornecedor_id = _cria_fornecedor(conexao)
    categoria_id = _cria_categoria(conexao)
    produto_id = _cria_produto(conexao, categoria_id, fornecedor_id)

    saldo = conexao.execute(
        select(TABELAS["produtos"].c.quantidade_em_estoque).where(
            TABELAS["produtos"].c.id == produto_id
        )
    ).scalar_one()
    assert saldo == 0


def test_referencias_precisam_existir(conexao):
    _deve_falhar(
        conexao,
        TABELAS["produtos"],
        nome="Órfão",
        sku="SKU-X",
        preco_custo="1.00",
        preco_venda="2.00",
        categoria_id=9999,
        fornecedor_id=9999,
    )


def test_movimentacao_quantidade_positiva(conexao):
    fornecedor_id = _cria_fornecedor(conexao)
    categoria_id = _cria_categoria(conexao)
    produto_id = _cria_produto(conexao, categoria_id, fornecedor_id)

    _deve_falhar(
        conexao,
        TABELAS["movimentacoes"],
        produto_id=produto_id,
        tipo=TipoMovimentacao.ENTRADA,
        quantidade=0,
    )
    conexao.execute(
        insert(TABELAS["movimentacoes"]).values(
            produto_id=produto_id, tipo=TipoMovimentacao.SAIDA, quantidade=1
        )
    )


def test_vinculos_impedem_exclusao_restrict(conexao):
    fornecedor_id = _cria_fornecedor(conexao)
    categoria_id = _cria_categoria(conexao)
    produto_id = _cria_produto(conexao, categoria_id, fornecedor_id)

    with pytest.raises(IntegrityError), conexao.begin_nested():
        conexao.execute(
            delete(TABELAS["categorias"]).where(TABELAS["categorias"].c.id == categoria_id)
        )
    with pytest.raises(IntegrityError), conexao.begin_nested():
        conexao.execute(
            delete(TABELAS["fornecedores"]).where(TABELAS["fornecedores"].c.id == fornecedor_id)
        )

    conexao.execute(
        insert(TABELAS["movimentacoes"]).values(
            produto_id=produto_id, tipo=TipoMovimentacao.ENTRADA, quantidade=1
        )
    )
    with pytest.raises(IntegrityError), conexao.begin_nested():
        conexao.execute(delete(TABELAS["produtos"]).where(TABELAS["produtos"].c.id == produto_id))
