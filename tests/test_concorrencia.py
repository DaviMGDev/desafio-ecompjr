"""Prova que o lock pessimista impede saldo incorreto sob requisições simultâneas.

Diferente dos demais testes, este usa sessões reais em conexões distintas (sem a
transação revertida das fixtures): concorrência de verdade precisa de conexões
de verdade. Os dados criados são removidos ao final de cada teste.
"""

import threading
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import delete, func, select

from app.db import SessionLocal
from app.models import Categoria, Fornecedor, Movimentacao, Produto
from app.schemas.movimentacao import MovimentacaoCreate
from app.services import movimentacoes


def _criar_produto_real(saldo: int) -> tuple[int, int, int]:
    with SessionLocal() as session:
        categoria = Categoria(nome="Concorrência")
        fornecedor = Fornecedor(
            nome="Fornecedor Concorrência",
            cnpj="11222333000181",
            telefone="1",
            email="concorrencia@exemplo.com",
        )
        session.add_all([categoria, fornecedor])
        session.flush()
        produto = Produto(
            nome="Produto Concorrência",
            sku="SKU-CONC",
            preco_custo=Decimal("1.00"),
            preco_venda=Decimal("2.00"),
            quantidade_em_estoque=saldo,
            categoria_id=categoria.id,
            fornecedor_id=fornecedor.id,
        )
        session.add(produto)
        session.commit()
        return produto.id, fornecedor.id, categoria.id


def _limpar(produto_id: int, fornecedor_id: int, categoria_id: int) -> None:
    with SessionLocal() as session:
        session.execute(delete(Movimentacao).where(Movimentacao.produto_id == produto_id))
        session.execute(delete(Produto).where(Produto.id == produto_id))
        session.execute(delete(Fornecedor).where(Fornecedor.id == fornecedor_id))
        session.execute(delete(Categoria).where(Categoria.id == categoria_id))
        session.commit()


def _saldo(produto_id: int) -> int:
    with SessionLocal() as session:
        return session.scalar(
            select(Produto.quantidade_em_estoque).where(Produto.id == produto_id)
        )


def _total_movimentacoes(produto_id: int) -> int:
    with SessionLocal() as session:
        return session.scalar(
            select(func.count())
            .select_from(Movimentacao)
            .where(Movimentacao.produto_id == produto_id)
        )


def _disparar(produto_id: int, tipo: str, quantidade: int) -> list[str]:
    """Dispara duas movimentações iguais em threads separadas, com barreira.

    A barreira sincroniza a partida para maximizar a sobreposição das duas
    transações (o cenário de race condition do enunciado § 3.c).
    """
    barreira = threading.Barrier(2)
    resultados: list[str] = []

    def executar() -> None:
        with SessionLocal() as session:
            barreira.wait()
            try:
                movimentacoes.criar(
                    session,
                    MovimentacaoCreate(produto_id=produto_id, tipo=tipo, quantidade=quantidade),
                )
                resultados.append("sucesso")
            except HTTPException as exc:
                resultados.append(f"erro_{exc.status_code}")

    threads = [threading.Thread(target=executar) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return sorted(resultados)


def test_saidas_concorrentes_com_saldo_para_uma():
    produto_id, fornecedor_id, categoria_id = _criar_produto_real(saldo=5)
    try:
        resultados = _disparar(produto_id, "saida", 4)

        assert resultados == ["erro_409", "sucesso"]
        assert _saldo(produto_id) == 1
        assert _total_movimentacoes(produto_id) == 1
    finally:
        _limpar(produto_id, fornecedor_id, categoria_id)


def test_saidas_concorrentes_dentro_do_saldo_somam_corretamente():
    produto_id, fornecedor_id, categoria_id = _criar_produto_real(saldo=10)
    try:
        resultados = _disparar(produto_id, "saida", 4)

        assert resultados == ["sucesso", "sucesso"]
        assert _saldo(produto_id) == 2
        assert _total_movimentacoes(produto_id) == 2
    finally:
        _limpar(produto_id, fornecedor_id, categoria_id)


def test_entradas_concorrentes_somam_todas():
    produto_id, fornecedor_id, categoria_id = _criar_produto_real(saldo=0)
    try:
        resultados = _disparar(produto_id, "entrada", 7)

        assert resultados == ["sucesso", "sucesso"]
        assert _saldo(produto_id) == 14
        assert _total_movimentacoes(produto_id) == 2
    finally:
        _limpar(produto_id, fornecedor_id, categoria_id)
