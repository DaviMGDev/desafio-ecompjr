# language: pt
# Fonte: enunciado § 2.b (nome único) e § 2.c (exclusão com produtos).
@obrigatorio
Funcionalidade: Catálogo de categorias
  Para classificar os produtos, preciso manter categorias únicas e impedir a
  exclusão de categoria ainda usada.

  Regra: Nome único, ignorando maiúsculas/minúsculas

    Cenário: Cadastro de categoria válida
      Quando envio um POST /categorias com nome "Bebidas"
      Então a resposta tem status 201

    Esquema do Cenário: Nome já existente
      Dado que existe categoria com nome "<existente>"
      Quando envio um POST /categorias com nome "<novo>"
      Então a resposta tem status 409

      Exemplos:
        | existente | novo    |
        | Bebidas   | Bebidas |
        | Bebidas   | bebidas |

  Regra: Categoria com produtos vinculados não pode ser excluída (§ 2.c)

    Cenário: Exclusão de categoria vazia
      Dado que existe categoria sem produtos
      Quando envio um DELETE /categorias/{id}
      Então a resposta tem status 204

    Cenário: Exclusão de categoria com produtos
      Dado que existe categoria com um produto vinculado
      Quando envio um DELETE /categorias/{id}
      Então a resposta tem status 409
      E o corpo contém mensagem explicando que há produtos vinculados
      E a categoria continua existindo

  Regra: Leitura e edição

    Cenário: Listagem de categorias
      Quando envio um GET /categorias
      Então a resposta tem status 200
      E o corpo é uma lista paginada de categorias

    Cenário: Categoria inexistente
      Quando envio um GET /categorias/{id} com id inexistente
      Então a resposta tem status 404

    Cenário: Renomear categoria para nome já usado
      Dado que existem as categorias "Bebidas" e "Limpeza"
      Quando envio um PUT /categorias/{id de Limpeza} com nome "Bebidas"
      Então a resposta tem status 409
