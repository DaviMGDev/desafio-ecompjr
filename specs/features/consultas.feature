# language: pt
# Fonte: enunciado § 2.d (estoque mínimo; filtros de período e fornecedor).
@obrigatorio
Funcionalidade: Consultas avançadas de estoque
  Para agir antes de perder venda, quero ver produtos no/abaixo do mínimo e
  filtrar o histórico de movimentações.

  Regra: Produtos em/abaixo do estoque mínimo

    Cenário: Produto no limite entra na consulta
      Dado que existe produto com saldo 3 e mínimo 3
      Quando envio um GET /produtos/estoque-baixo
      Então a resposta tem status 200
      E o produto aparece no resultado com saldo e mínimo

    Cenário: Produto abaixo do mínimo entra na consulta
      Dado que existe produto com saldo 1 e mínimo 5
      Quando envio um GET /produtos/estoque-baixo
      Então o produto aparece no resultado

    Cenário: Produto acima do mínimo fica fora
      Dado que existe produto com saldo 10 e mínimo 2
      Quando envio um GET /produtos/estoque-baixo
      Então o produto não aparece no resultado

    Cenário: Sem produtos críticos
      Dado que nenhum produto está no/abaixo do mínimo
      Quando envio um GET /produtos/estoque-baixo
      Então a resposta tem status 200
      E o corpo é uma lista vazia

  Regra: Filtro de movimentações por período (inclusivo)

    Cenário: Período recorta o histórico
      Dado que existem movimentações em datas distintas
      Quando envio um GET /movimentacoes com data_inicio e data_fim cobrindo
        apenas parte do período
      Então a resposta tem status 200
      E somente as movimentações do período aparecem
      E as datas nos limites são incluídas

    Cenário: Período invertido
      Quando envio um GET /movimentacoes com data_inicio maior que data_fim
      Então a resposta tem status 422

    Cenário: Data em formato inválido
      Quando envio um GET /movimentacoes com data_inicio "31/01/2026"
      Então a resposta tem status 422

  Regra: Filtro de movimentações por fornecedor

    Cenário: Fornecedor filtra pelo valor registrado na movimentação
      Dado que existem entradas registradas com fornecedores distintos
      Quando envio um GET /movimentacoes com fornecedor_id de um deles
      Então somente as movimentações desse fornecedor aparecem

    Cenário: Combinação de filtros
      Quando envio um GET /movimentacoes com fornecedor_id e período juntos
      Então somente as movimentações que atendem aos dois filtros aparecem

  Regra: Paginação

    Cenário: Listagem paginada
      Quando envio um GET /movimentacoes com limit 10 e offset 0
      Então a resposta tem status 200
      E o corpo traz no máximo 10 itens
