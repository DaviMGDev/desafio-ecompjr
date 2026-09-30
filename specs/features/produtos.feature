# language: pt
# Fonte: enunciado § 2.b (campos, sku único), § 2.c e § 2.d (estoque mínimo).
@obrigatorio
Funcionalidade: Cadastro de produtos
  Para que o catálogo reflita a loja, preciso manter produtos com preços,
  categoria e fornecedor, com SKU único e saldo somente leitura.

  Regra: SKU único

    Cenário: Cadastro válido
      Dado que existem uma categoria e um fornecedor cadastrados
      Quando envio um POST /produtos com nome, SKU "SKU-001", preço de custo,
        preço de venda, categoria e fornecedor
      Então a resposta tem status 201
      E o produto nasce com quantidade_em_estoque 0

    Cenário: SKU duplicado
      Dado que existe produto com SKU "SKU-001"
      Quando envio um POST /produtos com o mesmo SKU
      Então a resposta tem status 409
      E nenhum produto novo é criado

  Regra: Saldo só muda por movimentação

    Cenário: Criar produto enviando saldo
      Quando envio um POST /produtos com o campo quantidade_em_estoque
      Então a resposta tem status 422

    Cenário: Editar produto tentando alterar saldo
      Dado que existe produto com saldo 10
      Quando envio um PUT /produtos/{id} com quantidade_em_estoque 999
      Então a resposta tem status 422
      E o saldo do produto continua 10

  Regra: Categoria e fornecedor referenciados precisam existir

    Cenário: Categoria inexistente
      Quando envio um POST /produtos com categoria_id inexistente
      Então a resposta tem status 404
      E o corpo contém mensagem explicativa

    Cenário: Fornecedor inexistente
      Quando envio um POST /produtos com fornecedor_id inexistente
      Então a resposta tem status 404

  Regra: Valores e exclusão

    Esquema do Cenário: Valores inválidos são recusados
      Quando envio um POST /produtos com <campo> igual a <valor>
      Então a resposta tem status 422

      Exemplos:
        | campo             | valor |
        | preco_custo       | -1    |
        | preco_venda       | -1    |
        | quantidade_minima | -5    |

    Cenário: Produto com movimentações não pode ser excluído
      Dado que existe produto com movimentação registrada
      Quando envio um DELETE /produtos/{id}
      Então a resposta tem status 409
      E o produto continua existindo

    Cenário: Produto sem movimentações pode ser excluído
      Dado que existe produto sem movimentações
      Quando envio um DELETE /produtos/{id}
      Então a resposta tem status 204
