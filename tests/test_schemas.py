"""Cobre validadores e regras de payload dos schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.fornecedor import FornecedorCreate
from app.schemas.movimentacao import MovimentacaoCreate
from app.schemas.produto import ProdutoCreate


def _produto(**extra):
    dados = {
        "nome": "Produto",
        "sku": "SKU-1",
        "preco_custo": "10.00",
        "preco_venda": "15.00",
        "categoria_id": 1,
        "fornecedor_id": 1,
    }
    dados.update(extra)
    return ProdutoCreate(**dados)


def test_cnpj_com_mascara_e_normalizado_e_email_vira_minusculo():
    fornecedor = FornecedorCreate(
        nome="Loja", cnpj="11.222.333/0001-81", telefone="75999990000", email="Loja@Exemplo.com"
    )

    assert fornecedor.cnpj == "11222333000181"
    assert str(fornecedor.email) == "loja@exemplo.com"


def test_cnpj_invalido_e_recusado():
    with pytest.raises(ValidationError):
        FornecedorCreate(
            nome="Loja", cnpj="11.111.111/1111-11", telefone="1", email="loja@exemplo.com"
        )


def test_saldo_nao_e_aceito_no_payload_de_produto():
    with pytest.raises(ValidationError):
        _produto(quantidade_em_estoque=10)


def test_precos_negativos_sao_recusados():
    with pytest.raises(ValidationError):
        _produto(preco_custo="-1.00")


def test_movimentacao_quantidade_precisa_ser_positiva():
    with pytest.raises(ValidationError):
        MovimentacaoCreate(produto_id=1, tipo="entrada", quantidade=0)

    movimentacao = MovimentacaoCreate(produto_id=1, tipo="saida", quantidade=1)
    assert movimentacao.quantidade == 1
