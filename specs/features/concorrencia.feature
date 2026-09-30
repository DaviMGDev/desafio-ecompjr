# language: pt
# Fonte: enunciado § 3.c (race conditions) — diferencial.
# As definições de passo simulam concorrência com requisições paralelas
# (threads/sessões distintas) sobre o mesmo produto.
@diferencial
Funcionalidade: Concorrência no saldo
  Para impedir estoque negativo sob requisições simultâneas, a atualização de
  saldo usa transação com lock por produto.

  Regra: Saídas simultâneas não podem estourar o saldo

    Cenário: Duas saídas concorrentes com saldo para apenas uma
      Dado que existe produto com saldo 5
      Quando duas requisições de saída de 4 são enviadas ao mesmo tempo
      Então exatamente uma resposta tem status 201
      E a outra resposta tem status 409
      E o saldo final do produto é 1

    Cenário: Saídas concorrentes dentro do saldo somam corretamente
      Dado que existe produto com saldo 10
      Quando duas requisições de saída de 4 são enviadas ao mesmo tempo
      Então as duas respostas têm status 201
      E o saldo final do produto é 2

    Cenário: Entradas concorrentes somam todas
      Dado que existe produto com saldo 0
      Quando duas requisições de entrada de 7 são enviadas ao mesmo tempo
      Então as duas respostas têm status 201
      E o saldo final do produto é 14

    Cenário: Falha por saldo não deixa rastro
      Dado que existe produto com saldo 1
      Quando uma saída de 2 falha por saldo insuficiente
      Então nenhuma movimentação é criada
      E o saldo do produto continua 1
