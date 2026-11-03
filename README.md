# EcoHora — Reciclagem e participação acadêmica

Plataforma web desenvolvida como projeto acadêmico de ACEX da Fundação Santo André. O EcoHora busca incentivar práticas sustentáveis no ambiente estudantil por meio do registro de entregas de materiais recicláveis e da atribuição de pontos aos estudantes.

A proposta relaciona a participação em ações de reciclagem à possibilidade de aproveitamento em atividades complementares. **Na versão demonstrada, o fluxo implementado registra as entregas validadas e credita pontos; a conversão automática desses pontos em horas complementares não está implementada.**

## Objetivos

- Incentivar a participação dos estudantes em práticas de reciclagem;
- Facilitar a consulta de informações sobre materiais e pontos de coleta;
- Registrar e validar entregas de materiais recicláveis;
- Atribuir pontos de acordo com o material e o peso registrado;
- Apoiar a educação ambiental e a participação acadêmica.

## Funcionalidades

### Área do estudante

- Acesso por autenticação;
- Consulta do painel e da pontuação acumulada;
- Consulta ao histórico de entregas e ao peso reciclado;
- Consulta dos materiais aceitos e da pontuação por quilograma;
- Acesso ao fluxo de confirmação de entrega por QR Code;
- Consulta de eventos, grupos e informações de perfil.

### Área administrativa

- Acesso às funcionalidades administrativas conforme o perfil de usuário;
- Registro do material e do peso recebido;
- Geração de QR Code associado a uma entrega;
- Disponibilização do QR Code para confirmação pelo estudante.

### Fluxo de validação por QR Code

1. O administrador seleciona o material e informa o peso da entrega.
2. A plataforma gera um QR Code vinculado aos dados daquela entrega.
3. O estudante lê o código e acessa a página de confirmação.
4. O estudante confere as informações e confirma a entrega.
5. Após a validação, a entrega é registrada e os pontos correspondentes são creditados.

Os QR Codes possuem validade limitada. Na implementação atual, o prazo de expiração é de 10 minutos.

### Pontuação dos materiais

A pontuação é calculada por quilograma, conforme os valores configurados no sistema:

| Material | Pontos por kg |
| --- | ---: |
| Papel | 2 |
| Plástico | 2 |
| Metal | 1 |
| Vidro | 3 |

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Frontend | HTML, CSS e JavaScript |
| Backend / API | Python e FastAPI |
| Banco de dados | SQLite |
| Acesso assíncrono ao banco | aiosqlite |
| Autenticação | JWT e bcrypt |
| Geração de QR Code | qrcode e Pillow |
| Servidor ASGI | Uvicorn |

## Organização do repositório

```text
.
├── assets/        # Recursos visuais
├── backend/       # API, rotas, regras de negócio e testes
├── database/      # Arquivos e recursos relacionados ao banco de dados
├── diagrams/      # Diagramas do projeto
├── docs/          # Documentação
├── frontend/      # Interface web e recursos do cliente
├── presentation/  # Materiais de apresentação
└── prototype/     # Protótipos
```

## Execução e ambientes

O projeto possui frontend e backend separados. A interface web consome a API desenvolvida em FastAPI. As configurações de ambiente, endereços permitidos para comunicação e credenciais de serviços devem ser fornecidos por variáveis de ambiente ou pela configuração do ambiente de implantação.

Não publique credenciais, chaves, tokens ou dados pessoais no repositório.

## Contexto acadêmico

Projeto desenvolvido no âmbito da atividade ACEX da Fundação Santo André, relacionado à educação ambiental e ao incentivo à reciclagem entre estudantes.

## Integrantes

- Catherine Marinho Antonioli
- Diego Oller de Oliveira
- Ingrid Thaina Lima de Oliveira
- João Roberto Negri
- Leonardo José Alves Gouvea
- Matheus Adryel Franzoni

## Status

Projeto acadêmico em desenvolvimento. As funcionalidades disponíveis devem ser consideradas dentro do escopo da versão implementada e demonstrada.
