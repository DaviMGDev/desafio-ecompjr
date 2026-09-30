# language: pt
# Fonte: enunciado § 2.b e § 2.c (imutabilidade e reflexo automático no saldo).
@obrigatorio
Funcionalidade: Movimentação de estoque
  Para auditar entradas e saídas, registro movimentações imutáveis que atualizam
  o saldo do produto na mesma transação.

  Regra: Entrada soma ao saldo

    Cenário: Entrada em produto existente
      Dado que existe produto com saldo 5
      Quando envio um POST /movimentacoes de entrada com quantidade 3
      Então a resposta tem status 201
      E o saldo do produto passa a 8
      E a movimentação guarda produto, tipo, quantidade e data

  Regra: Saída subtrai do saldo; saldo não fica negativo

    Cenário: Saída dentro do saldo
      Dado que existe produto com saldo 5
      Quando envio um POST /movimentacoes de saída com quantidade 2
      Então a resposta tem status 201
      E o saldo do produto passa a 3

    Cenário: Saída maior que o saldo
      Dado que existe produto com saldo 2
      Quando envio um POST /movimentacoes de saída com quantidade 3
      Então a resposta tem status 409
      E o corpo contém mensagem de saldo insuficiente
      E o saldo do produto continua 2
      E nenhuma movimentação é criada

  Regra: Movimentação é imutável

    Cenário: Alterar movimentação
      Dado que existe uma movimentação registrada
      Quando envio um PUT /movimentacoes/{id}
      Então a resposta tem status 405

    Cenário: Excluir movimentação
      Dado que existe uma movimentação registrada
      Quando envio um DELETE /movimentacoes/{id}
      Então a resposta tem status 405
      E a movimentação continua consultável

  Regra: Validação do payload

    Esquema do Cenário: Payload inválido
      Quando envio um POST /movimentacoes com <campo> igual a <valor>
      Então a resposta tem status 422

      Exemplos:
        | campo      | valor          |
        | quantidade | 0              |
        | quantidade | -1             |
        | tipo       | "transferencia" |

    Cenário: Produto inexistente
      Quando envio um POST /movimentacoes para produto_id inexistente
      Então a resposta tem status 404

    Cenário: Data definida pelo servidor
      Quando envio um POST /movimentacoes sem data
      Então a movimentação criada tem data preenchida pelo servidor
