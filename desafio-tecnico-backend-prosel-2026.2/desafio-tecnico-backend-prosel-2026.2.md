![EcompJr — Empresa Júnior de Computação da UEFS](assets/page-1-fig-1.png)

# Desafio Técnico - Trilha Back-End Prosel 2026.2

**API de Gerenciamento de Empresas Clientes**

## 1. Problema

Um dos atuais clientes que a Ecomp Jr. possui é a “愚公移山 Variedades”, que possui múltiplos fornecedores e um catálogo diverso de produtos importados. A sua organização de estoque é realizada totalmente de forma escrita, modalidade essa que impacta diretamente na venda de seus artigos. Uma das grandes debilidades desse sistema se dá na incapacidade de criar relações, já que, a loja precisa saber quem é o fornecedor do(s) produto(s) e a categoria do(s) mesmo(s), além de auditar o histórico de entradas/saídas do estoque.

Nesse contexto, a empresa irá desenvolver um sistema de estoque que concentre todas as informações em um único ambiente para essa loja de variedades. O núcleo desse sistema será uma API, responsável por organizar e disponibilizar os dados de forma padronizada, garantindo que futuras aplicações web e mobile tenham acesso a informações consistentes, atualizadas e confiáveis.

Como futuro(a) desenvolvedor(a) Back-end da Ecomp Jr., seu papel será projetar e implementar essa API, contemplando funcionalidades essenciais de auditoria de estoque e cadastro, consulta, edição e exclusão de informações sobre fornecedores, produtos e suas categorias, permitindo que a loja gerencie tudo de maneira mais eficiente e estratégica.

## 2. Requisitos Obrigatórios

### a. Tecnologias Fast API e PostgreSQL

Utilizar FastAPI para a construção da API e PostgreSQL para o armazenamento dos dados.

### b. Modelagem de Dados

As entidades principais são: Produto, Fornecedor, Categoria e Movimentação de Estoque.

A entidade Produto deve conter, no mínimo, os seguintes campos: id, nome, sku/código (único), preço_custo, preço_venda, quantidade_em_estoque, data_cadastro. Já para a entidade Fornecedor, deve-se ter, no mínimo: id, nome, cnpj (único), telefone, email. Para garantir a integridade dos dados, os campos cnpj e email devem ser únicos no banco de dados, evitando o cadastro de fornecedores com informações duplicadas.

A entidade Categoria deve conter, no mínimo: id e nome (único), servindo para classificar os produtos cadastrados.

A entidade Movimentação de Estoque deve conter, no mínimo: id, tipo (entrada ou saída), quantidade e data. Diferente das demais entidades, os registros de Movimentação são imutáveis: uma vez criados, não devem ser passíveis de edição ou exclusão pela API, apenas de criação e consulta, servindo como histórico de auditoria confiável do estoque.

Cabe a você definir como estruturar os relacionamentos entre essas entidades de forma a garantir a integridade referencial dos dados.

### c. Funcionalidades de CRUD (Create, Read, Update, Delete)

A API deve garantir o gerenciamento completo das entidades modeladas. Você deverá projetar os endpoints para criar, ler, atualizar e excluir os registros. A implementação exata fica a seu critério, mas você deverá prestar atenção às regras de negócio e à integridade dos dados: considere atentamente o que deve acontecer ao tentar excluir uma categoria que ainda contém produtos, ou como a inserção de um log de movimentação deve refletir automaticamente na quantidade de estoque disponível.

### d. Funcionalidades de Consulta Avançada

Um sistema de estoque eficiente vai além da simples leitura de todos os dados. Você deverá implementar endpoints de pesquisa avançada que agreguem valor estratégico à loja. Como você estruturaria uma consulta (query) para identificar imediatamente os produtos que atingiram o estoque mínimo? Como você permitiria a filtragem do histórico de movimentações por um período de tempo específico ou por um determinado fornecedor? Desenvolva os filtros que julgar essenciais.

### e. Tratamento de Erros

A API será o núcleo de futuras aplicações web e mobile e deve comunicar os problemas de forma clara e padronizada. Não serão aceitos "stack traces" expostos no retorno da API ou o uso indevido de códigos de status 200 para requisições falhas. Você deve estruturar um modelo de resposta para exceções que retorne o código HTTP apropriado (ex: 400 para dados inválidos, 404 para recursos não encontrados, 500 para erros internos do servidor) acompanhado de uma mensagem explicativa compreensível.

### f. Commits Padronizados no GitHub

O uso do Git será avaliado, pois o trabalho em equipe exige rastreabilidade:

- **Progresso incremental:** É obrigatório que o desenvolvimento mostre um progresso contínuo e distribuído ao longo das 4 semanas do projeto.
- **Convenção:** É exigido o uso obrigatório da convenção de Conventional Commits. Cada commit deve apresentar um prefixo semântico (como feat:, fix:, docs:, refactor:) e uma mensagem descritiva e significativa que ilustre com precisão o conteúdo da alteração, facilitando a auditoria e o rastreamento das funcionalidades implementadas. [(Não sabe o que é?)](https://www.conventionalcommits.org/pt-br/v1.0.0-beta.4/)

### g. Documentação da API e comentários coerentes

- **Documentação da API:** É obrigatório documentar cada endpoint. Pode-se utilizar ferramentas de mercado como Swagger/OpenAPI, ou fornecer dentro do repositório uma Collection exportada (Postman ou Insomnia) acompanhada de um arquivo README.md extremamente detalhado. A documentação deve incluir para cada rota: método HTTP, caminho da URL, eventuais parâmetros de query ou path, a estrutura esperada do body (com exemplos em JSON) e as respostas previstas para casos de sucesso (2xx) e de erro (4xx, 5xx), incluindo os códigos de status e os JSONs de retorno.
- **Comentários no Código:** Aplique o princípio do código limpo (*clean code*): o código deve explicar "o que" faz, os comentários devem explicar "por que" o faz. Utilize os comentários exclusivamente para justificar decisões arquiteturais, blocos de lógica de negócios complexos ou o motivo pelo qual uma determinada abordagem foi escolhida (por exemplo, o gerenciamento de transações no banco de dados durante uma atualização de estoque).

## 3. Diferenciais

Os itens abaixo são inteiramente opcionais e não são pré-requisito para uma boa avaliação. Um(a) candidato(a) que implemente com excelência apenas os requisitos obrigatórios das seções 2 e 5 já demonstra uma base técnica sólida e competitiva. Os diferenciais servem para o(a) candidato(a) que quer se destacar e aprender conceitos novos e amplamente usados no mercado — não é esperado que todos saibam ou tenham tempo para implementá-los durante o desafio.

### a. Autenticação e Segurança (0,5)

A implementação de um sistema de gerenciamento de estoque exige que o acesso aos dados sensíveis da empresa seja rigorosamente protegido. Um excelente diferencial consiste em implementar um mecanismo de segurança para a API. Como você garantiria que apenas usuários autorizados pudessem interagir com o sistema? A adoção de padrões consolidados (como JWT) para proteger as rotas e a estruturação de um sistema de autorização baseado em funções (por exemplo, distinguindo as permissões de leitura de um funcionário daquelas de administração do catálogo) demonstrarão uma compreensão avançada de segurança no Back-end.

### b. Testes Automatizados (0,5)

Garantir a confiabilidade da API é fundamental antes que os dados sejam consumidos por interfaces externas. Será avaliada de forma muito positiva a capacidade de validar a lógica de negócios e o funcionamento correto dos endpoints sem depender de testes manuais repetitivos. Um candidato de destaque não se limitará a escrever os testes, mas saberá estruturá-los de forma lógica, configurando pipelines de validação e workflows automatizados diretamente no repositório para garantir que a integração de novos códigos não comprometa as funcionalidades já estáveis.

### c. Gerenciamento de Concorrência (Condições de Corrida / Race Conditions) (1)

Em um ambiente real, vários vendedores ou sistemas podem tentar registrar a saída do mesmo produto simultaneamente. Como você evita que duas requisições simultâneas ignorem o controle de quantidade, levando a um estoque negativo ou a um cálculo incorreto de inventário? Este é um problema crítico de concorrência. A implementação de estratégias para evitar condições de corrida, como o uso de transações de banco de dados bem modeladas e mecanismos de bloqueio de registros (otimista ou pessimista), demonstrará sua capacidade de projetar arquiteturas para cenários de produção complexos.

## 4. Produto

Espera-se que o produto final seja uma API completa, bem documentada, segura e eficiente para os donos da loja de variedades. A API deve ser intuitiva de usar através de sua documentação e robusta o suficiente para servir como base para diversas aplicações.

## 5. Entrega

O prazo para entrega do produto vai até o dia **16/10/2026**, via e-mail (ecompjr@uefs.br) contendo o link do repositório do projeto no github. A data da defesa do projeto será definida de acordo com a disponibilidade do candidato.

## 6. Barema

Ressaltamos que o uso de ferramentas de Inteligência Artificial (IA) durante o desenvolvimento não é proibido — pelo contrário, faz parte do repertório de um(a) desenvolvedor(a) atual. No entanto, a avaliação não se limita ao código final entregue: haverá uma etapa de defesa técnica, na qual o(a) candidato(a) deverá explicar e justificar as decisões tomadas em seu próprio projeto. Soluções que não puderem ser explicadas ou justificadas pelo(a) candidato(a) — indicando ausência de compreensão real sobre a arquitetura, as regras de negócio ou as decisões implementadas — serão penalizadas nos critérios de Qualidade do Código e Documentação, podendo resultar em desclassificação em casos de completa incapacidade de defender o próprio trabalho.

A nota final será calculada pela soma dos pontos obtidos em cada critério de avaliação, conforme os pesos definidos no Barema. O resultado será um valor entre 0 e 8, com a pontuação máxima limitada a 10 contabilizando com os extras.

| Critério | Descrição do critério | Nota |
|----------|------------------------|------|
| Documentação e Comentários | Avalia a clareza e qualidade da documentação da API (Swagger/OpenAPI ou Collection + README) e a coerência dos comentários no código, conforme os critérios da seção 2.g. | De 0 a 1 |
| CRUD de Entidades | Avalia a implementação completa das funcionalidades de criar, ler, atualizar e excluir Produtos, Fornecedores e Categorias, incluindo o tratamento correto das regras de negócio (ex: restrição de exclusão de categorias com produtos vinculados) e o registro de Movimentações de Estoque, respeitando sua imutabilidade. | De 0 a 1 |
| Consultas Avançadas | Avalia a implementação dos endpoints de pesquisa estratégica: identificação de produtos com estoque no mínimo ou abaixo dele, e filtragem do histórico de movimentações por período e/ou fornecedor. | De 0 a 1 |
| Mensagens de Erros | Avalia a implementação de um modelo de resposta padronizado para exceções, com os códigos HTTP apropriados (400, 404, 500) e mensagens explicativas, sem exposição de stack traces ou uso indevido de status 200 em falhas. | De 0 a 1 |
| Commits Padronizados | Avalia o uso da convenção de Conventional Commits e a evidência de progresso incremental e distribuído ao longo das 4 semanas do desafio, conforme a seção 2.f. | De 0 a 2 |
| Qualidade de Código | Avalia a organização do projeto, a clareza do código, a aplicação de boas práticas de desenvolvimento e o correto gerenciamento de transações em operações que envolvem múltiplas entidades. **A nota considera a capacidade do(a) candidato(a) de explicar e justificar as próprias decisões técnicas durante a defesa.** | De 0 a 2 |
| Diferenciais (extra) | Avalia a implementação de um ou mais dos diferenciais propostos (Autenticação e Segurança, Testes Automatizados, Gerenciamento de Concorrência), com pontuação proporcional conforme os pesos individuais definidos na seção 3. | De 0 a 2 (0,5 + 0,5 + 1) |

## 7. Dicas e Recomendações

Sabemos que desenvolver uma API é algo complexo e trabalhoso. Por isso, separamos algumas dicas e recomendações que podem ajudar a desenvolver o sistema:

### 1. Uso de Inteligência Artificial

O uso de ferramentas de IA (ChatGPT, Cursor, Copilot, Claude, etc.) é permitido e esperado — faz parte do repertório de um(a) desenvolvedor(a) atual. Para que essa ferramenta realmente contribua com seu aprendizado (e sua nota na defesa técnica), recomendamos:

- **a. Use a IA para entender, não só para gerar.** Peça explicações do "porquê" antes de aceitar o "como" — ex: "por que essa abordagem evita race condition?" em vez de só "resolva o race condition pra mim".
- **b. Nunca cole um trecho de código que você não conseguiria explicar em voz alta.** Se não sabe reescrever aquela função sem consultar a IA de novo, ainda não está pronto — revise até entender.
- **c. Use a IA como par de debug, não como autopilot.** É muito mais valioso usá-la pra investigar um erro específico do que pedir pra gerar o endpoint inteiro de uma vez.
- **d. Desconfie de soluções "perfeitas" demais.** Muitas vezes a IA sugere abordagens genéricas que não consideram as regras de negócio específicas deste desafio (ex: a imutabilidade da Movimentação de Estoque). Sempre valide contra o enunciado.
- **e. Lembre-se:** haverá uma etapa de defesa técnica em que você precisará explicar e justificar suas próprias decisões — construa esse entendimento ao longo do processo, não na véspera.
- **f. DICA EXTRA:** Considere usar [AGENTS.md](http://agents.md) para o desenvolvimento.

### 2. Ambiente Virtual (venv)

Sempre utilize ambientes virtuais em Python para gerenciar as dependências do seu projeto de forma isolada e organizada.

### 3. Documentação do FastAPI

A documentação oficial do FastAPI é sua maior aliada. Ela é completa, didática e possui exemplos para quase tudo que você precisará fazer.

### 4. SQLAlchemy ORM e Alembic

Utilize o SQLAlchemy para a comunicação entre sua aplicação e o banco de dados — ele simplifica as operações e previne erros comuns. Recomendamos fortemente usar também o **Alembic** desde o início do projeto para versionar as alterações no schema do banco (migrations), em vez de recriar o banco do zero a cada mudança de modelo.

### 5. Postman / Insomnia

Utilize ferramentas como o Postman ou Insomnia para testar cada uma das suas rotas de forma manual, garantindo que elas funcionem como o esperado.

### 6. Playlists e vídeos recomendados

Aqui vai alguns materiais sugeridos que podem servir de guia para você no desenvolvimento do projeto.

- **a. [FastAPI do Zero (Hashtag Programação)](https://www.youtube.com/playlist?list=PLpdAy0tYrnKy3TvpCT-x7kGqMQ5grk1Xq):** — curso completo em português, do básico até deploy. As aulas sobre autenticação e autorização com JWT usando FastAPI, testes do sistema de autenticação com refresh token e automação de testes com integração contínua via GitHub Actions são especialmente úteis pros diferenciais deste desafio.
- **b. [Como Usar Agentes de IA para Aprender e Construir Seu Projeto Final](https://www.youtube.com/watch?v=vHersq7pBRE):** — Live realizada pelo Head of Education da Dio dando dicas a respeito de desenvolvimento de projetos com o uso de IA.
- **c. [Migrações, bancos de dados evolutivos (Alembic e SQLAlchemy) — Live de Python #211](https://www.youtube.com/watch?v=yQtqkq9UkDA):** — boa introdução em português aos conceitos de migrations e por que elas importam num projeto real.
- **d. Sobre concorrência e race conditions:** o artigo [Race Conditions e Locks: Garantindo a Integridade das Transações](https://dev.to/lerian/race-conditions-e-locks-garantindo-a-integridade-das-transacoes-financeiras-24b3) explica bem, com exemplo prático, a diferença entre lock otimista (bloqueia apenas na escrita, verificando conflito no commit) e lock pessimista (bloqueia leitura e escrita até o processamento terminar) — conceito direto para o diferencial de Gerenciamento de Concorrência.
- **e. Conventional Commits:** consulte a especificação oficial em [conventionalcommits.org](https://www.conventionalcommits.org/pt-br/v1.0.0/) (já disponível em português) — é a referência mais confiável e direta, sem depender de interpretação de terceiros.
