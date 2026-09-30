# language: pt
# Fonte: enunciado § 2.b (campos e unicidade) e § 2.c (integridade).
@obrigatorio
Funcionalidade: Cadastro de fornecedores
  Para que a loja saiba quem fornece cada produto, preciso criar, consultar,
  atualizar e excluir fornecedores com CNPJ e e-mail únicos.

  Regra: CNPJ e e-mail são únicos no banco

    Cenário: Cadastro de fornecedor válido
      Quando envio um POST /fornecedores com nome, CNPJ válido, telefone e e-mail
      Então a resposta tem status 201
      E o corpo contém o id do fornecedor criado
      E o CNPJ é armazenado sem máscara

    Cenário: CNPJ já cadastrado
      Dado que existe fornecedor com CNPJ "11222333000181"
      Quando envio um POST /fornecedores com o mesmo CNPJ
      Então a resposta tem status 409
      E o corpo contém mensagem explicando o conflito
      E nenhum fornecedor novo é criado

    Cenário: E-mail já cadastrado
      Dado que existe fornecedor com e-mail "fornecedor@exemplo.com"
      Quando envio um POST /fornecedores com o mesmo e-mail
      Então a resposta tem status 409

    Cenário: CNPJ com dígitos verificadores inválidos
      Quando envio um POST /fornecedores com CNPJ "11111111111111"
      Então a resposta tem status 422
      E o corpo contém mensagem de validação

  Regra: Fornecedor com produtos vinculados não pode ser excluído

    Cenário: Exclusão de fornecedor livre
      Dado que existe fornecedor sem produtos vinculados
      Quando envio um DELETE /fornecedores/{id} desse fornecedor
      Então a resposta tem status 204

    Cenário: Exclusão de fornecedor com produto vinculado
      Dado que existe fornecedor com um produto vinculado
      Quando envio um DELETE /fornecedores/{id} desse fornecedor
      Então a resposta tem status 409
      E o corpo contém mensagem explicando o vínculo
      E o fornecedor continua existindo

  Regra: Consulta e edição

    Cenário: Fornecedor inexistente
      Quando consulto um GET /fornecedores/{id} com id inexistente
      Então a resposta tem status 404
      E o corpo contém mensagem explicativa

    Cenário: Atualização de telefone
      Dado que existe fornecedor cadastrado
      Quando envio um PUT /fornecedores/{id} alterando o telefone
      Então a resposta tem status 200
      E o corpo mostra o telefone atualizado
