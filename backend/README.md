# Backend
O Backend do projeto é construído em Python utilizando uma forte documentação e boas práticas de segurança, com comentários para melhor entendimento.

A estrutura é baseada em uma REST API, fruto da biblioteca FastAPI, que cria uma fonte de documentação automática, além de rotas regradas para cada tipo de função. 

Foi optado por introduzir e manter a construção do banco de dados com SQLite, para manipulação rápida enquanto primeiros passos.

O Backend consiste em funções assíncronas para garantir fluidez e evitar o travamento do sistema em múltiplos processos.

## Bibliotecas usadas

### Bibliotecas Nativas do Python
* `os` - Foi usado para navegar entre os arquivos de modo seguro entre sistemas operacionais diferentes, além de garantir precisão.

* `re` - Utilizado para criar regras específicas de validação de texto que o Pydantic não cobria naturalmente.

* `asyncio` - Foi utilizada para rodar partes do programa durante testes devido à sua construção assíncrona.

* `importlib` - Foi usado para ler e otimizar importações de arquivos de rotas, devido à modularização do projeto para organização.

### Bibliotecas importadas
As bibliotecas externas importadas, e suas dependências, podem ser encontradas em requirements.txt.

* `aiosqlite` - Embora o Python possua a biblioteca nativa `sqlite3`, foi optado por utilizar o aiosqlite para funcionamento assíncrono.

* `bcrypt` - Foi fundamentalmente usada para criar uma espécie de máscara para as senhas dos usuários, chamada de `hash`, para impedir que mesmo os desenvolvedores possam ver senhas de usuários, além de dificultar ataques como brute force, criando curvas de tempo diferentes e o `salt` que cria uma aleatoriedade própria para cada senha através de um conjunto de caracteres inseridos juntamente à senha.

* `fastapi` - Foi escolhida para garantir segurança e estabilidade do projeto, cria o alicerce do Backend, fundando a API em si, com uma documentação automática, fácil de realizar testes e regras de rotas claras.

* `pydantic` - Foi fundamentalmente utilizado para criar regras de validação, promessas de resposta e esquemas legíveis, tanto para as requisições, quanto para as respostas, possibilitando uma dupla validação para o Frontend.

## Tecnologias usadas no Backend
* `Discloud` - Foi utilizada uma hospedagem fornecida pela Discloud, adquirindo um plano de assinatura mensal, para manter o projeto. [Discloud](https://discloud.com/)

* `Python` - A linguagem base do Backend, escolhida por afinidade e facilidade de análise e manipulação de dados, além de oferecer um excelente suporte para as finalidades já listadas.

* `SQLite` - Foi escolhido para construirmos o nosso Banco de Dados devido à sua manipulação ágil e facilitada.