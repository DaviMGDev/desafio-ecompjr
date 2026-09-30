# language: pt
# Fonte: enunciado § 2.e (modelo padronizado, HTTP correto, sem stack trace).
@obrigatorio
Funcionalidade: Tratamento padronizado de erros
  Para que aplicações consumidoras tratem falhas com segurança, toda resposta de
  erro segue um envelope único, com status correto e sem detalhes internos.

  Regra: Envelope único

    Cenário: Erro de negócio traz apenas detail
      Dado que existe fornecedor com CNPJ "11222333000181"
      Quando envio um POST /fornecedores com o mesmo CNPJ
      Então a resposta tem status 409
      E o corpo tem o campo "detail" com mensagem explicativa

    Cenário: Erro de validação traz detail com os campos
      Quando envio um POST /produtos sem nome
      Então a resposta tem status 422
      E o corpo tem "detail" com mensagem de validação

    Cenário: Recurso não encontrado
      Quando envio um GET /produtos/999999
      Então a resposta tem status 404
      E o corpo tem "detail" com mensagem explicativa

  Regra: Falha interna não vaza detalhes

    Cenário: Erro inesperado do servidor
      Dado que uma falha inesperada ocorre ao processar a requisição
      Quando a requisição termina
      Então a resposta tem status 500
      E o corpo tem "detail" com mensagem genérica
      E o corpo não contém stack trace

  Regra: Status correto, nunca 200 em falha

    Esquema do Cenário: Cada falha usa o status previsto na documentação
      Quando a requisição falha por <motivo>
      Então a resposta tem status <status>

      Exemplos:
        | motivo                | status |
        | validação de schema   | 422    |
        | recurso inexistente   | 404    |
        | conflito de unicidade | 409    |
        | vínculo de exclusão   | 409    |
        | saldo insuficiente    | 409    |
        | falha interna         | 500    |

    Cenário: Resposta de falha nunca é 200
      Quando uma requisição falha
      Então o status da resposta é diferente de 200
