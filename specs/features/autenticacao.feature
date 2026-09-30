# language: pt
# Fonte: enunciado § 3.a (JWT + autorização por perfis) — diferencial.
@diferencial
Funcionalidade: Autenticação e autorização
  Para proteger os dados da loja, a API exige token JWT e separa leitura de
  administração.

  Regra: Login emite token

    Cenário: Credenciais válidas
      Dado que existe usuário com perfil "admin"
      Quando envio um POST /auth/login com e-mail e senha corretos
      Então a resposta tem status 200
      E o corpo contém um token JWT
      E o token declara o perfil do usuário

    Cenário: Credenciais inválidas
      Quando envio um POST /auth/login com senha incorreta
      Então a resposta tem status 401

  Regra: Rotas protegidas

    Cenário: Requisição sem token
      Quando envio um GET /produtos sem cabeçalho Authorization
      Então a resposta tem status 401

    Cenário: Token inválido ou expirado
      Quando envio um GET /produtos com token inválido
      Então a resposta tem status 401

  Regra: Perfis

    Cenário: Perfil de leitura consulta
      Dado que estou autenticado com perfil "leitor"
      Quando envio um GET /produtos
      Então a resposta tem status 200

    Cenário: Perfil de leitura tenta escrever
      Dado que estou autenticado com perfil "leitor"
      Quando envio um POST /produtos
      Então a resposta tem status 403

    Cenário: Perfil de administração escreve
      Dado que estou autenticado com perfil "admin"
      Quando envio um POST /categorias com nome "Papelaria"
      Então a resposta tem status 201
