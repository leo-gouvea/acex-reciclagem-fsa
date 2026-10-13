#  💻 Backend - EcoHora ACEX

O Backend do projeto é desenvolvido em Python, fundamentado em uma documentação robusta, forte rigidez de segurança e aplicação de boas práticas de engenharia de software.

A estrutura é baseada em uma REST API, fruto da biblioteca FastAPI, que cria uma fonte de documentação automática, além de rotas regradas para cada tipo de função.

Optamos por utilizar o SQLite como banco de dados inicial para garantir agilidade na manipulação e facilitar os primeiros passos do desenvolvimento.

O Backend consiste em funções assíncronas para garantir fluidez e evitar o travamento do sistema em múltiplos processos.

## 📚 Bibliotecas usadas

### ⚙️ Bibliotecas Nativas do Python

* `os` 📂 — Usado para navegar entre os arquivos de modo seguro entre sistemas operacionais diferentes, além de garantir precisão.

* `re` 🔤 — Utilizado para criar regras específicas de validação de texto que o Pydantic não cobria naturalmente.

* `asyncio` ⏳ — Utilizada para rodar partes do programa durante testes devido à sua construção assíncrona.

* `importlib` 📦 — Usado para ler e otimizar importações de arquivos de rotas, devido à modularização do projeto para organização.

* `shutil` 📋 — Usada para manipulação de alto nível de arquivos — auxílio na integração de testes automatizados.

* `datetime` ⏰ — Usada para validação de dados de tempo, com ciência da atuação em UTC + 3 em relação ao Brasil.

### 🔌 Bibliotecas importadas

As bibliotecas externas importadas, e suas dependências, podem ser encontradas em `requirements.txt`.

* `aiosqlite` 🗄️ — Embora o Python possua a biblioteca nativa `sqlite3`, foi optado por utilizar o aiosqlite para funcionamento assíncrono.

* `bcrypt` 🔒 — Foi essencialmente usada para criar uma espécie de máscara para as senhas dos usuários, chamada de `hash`. Isso impede que até mesmo os desenvolvedores visualizem as senhas e dificulta ataques de *brute force*, criando curvas de tempo diferentes. Também aplica o *salt*, gerando uma aleatoriedade própria para cada senha.

* `fastapi` ⚡ — Escolhida para garantir segurança e estabilidade, ela estrutura o alicerce da API, fornecendo documentação automática, facilidade de testes e regras de rotas claras.

* `pydantic` 🛡️ — Foi principalmente utilizado para criar regras de validação, promessas de resposta e esquemas legíveis, tanto para requisições quanto para respostas, possibilitando uma dupla validação integrada ao Frontend.

* `dotenv` 🔑 — Foi utilizado para o carregamento de variáveis de ambiente e uso seguro de chaves de acesso.

* `pytest` 🧪 — Utilizado para criar scripts de automação de testes, facilitando na validação e homologação de processos de desenvolvimento.

* `PyJWT` 🎟️ — Utilizado para criar um fluxo de navegação com o frontend, fornecendo ferramentas para validações de permissão e autenticação.

## 🛠️ Tecnologias usadas no Backend

* `Python` 🐍 — A linguagem base do Backend, escolhida por afinidade, facilidade na manipulação de dados e excelente suporte para os requisitos do projeto.

* `SQLite` 🗃️ — Banco de dados escolhido devido à sua manipulação ágil, leveza e facilidade de configuração inicial.

* `Discloud` ☁️ — Foi utilizada uma hospedagem fornecida pela Discloud, adquirindo um plano de assinatura mensal, para manter o projeto ativo. [Discloud](https://discloud.com/)

* `Gemini` 🤖 — IA auxiliando no desenvolvimento de estruturas e guias nos processos de revisões + maturação de conteúdo.


# OBSERVAÇÃO:
Para um funcionamento adequado, permita que o site / app EcoHora gerencie Cookies de Terceiros, pelo menos quando em preview. Caso esteja negado, o login e sessão serão interrompidos.