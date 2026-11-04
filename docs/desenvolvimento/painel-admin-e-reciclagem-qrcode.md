# Painel administrativo e confirmação de reciclagem por QR Code

Esta documentação resume o que foi incluído na branch `feat/integracao-dashboard-qrcode`.

## O que foi feito

### Painel administrativo

Foi criada uma área separada para administradores, acessada por `frontend/admin.html`.

No painel, já estão disponíveis:

- **Visão geral:** quantidade de materiais cadastrados, pontuação por kg e destaque do primeiro colocado no ranking.
- **Materiais:** consulta dos materiais e da pontuação atribuída por quilo.
- **Ranking:** exibição dos alunos com suas pontuações, curso e turma.
- **Gerar QR Code:** formulário para selecionar o material e informar o peso da entrega.

O acesso ao painel verifica a sessão e o perfil do usuário. A autorização também é validada no backend; a checagem feita no JavaScript serve apenas para controlar a exibição da interface.

Algumas áreas administrativas aparecem como planejadas, mas ainda não estão ligadas a rotas funcionais: gerenciamento de usuários, pontos de coleta, auditoria completa das entregas, regras de conversão e relatórios.

### Entrega de recicláveis com QR Code

O fluxo de registro direto de reciclagem foi desativado. Agora, a entrega passa por duas etapas:

1. O administrador escolhe o material e informa o peso, entre 1 e 10 kg.
2. O backend cria uma entrega pendente e gera um QR Code com o link de confirmação.
3. O aluno entra na própria conta e abre o link.
4. A tela mostra o material, o peso, os pontos previstos e o horário de expiração.
5. O aluno confirma a entrega mantendo o botão pressionado.
6. O backend registra a entrega e credita os pontos na conta do aluno.

O QR Code tem validade de 10 minutos e só pode ser confirmado uma vez. O backend guarda o hash do token, em vez do token original, e verifica a validade e o perfil do usuário antes de concluir o registro.

A pontuação é calculada usando o valor cadastrado para cada material em pontos por quilo. O fluxo retorna os pontos recebidos na entrega e o total atualizado do aluno.

## Arquivos principais

| Arquivo | Responsabilidade |
|---|---|
| `frontend/admin.html` | Estrutura do painel administrativo |
| `frontend/admin.js` | Acesso, navegação, carregamento dos dados e geração do QR Code |
| `frontend/admin-api.js` | Chamadas da API usadas pelo painel |
| `frontend/confirmar-reciclagem.html` | Tela de confirmação da entrega |
| `frontend/confirmar-reciclagem.js` | Consulta e confirmação do QR Code |
| `frontend/estilos/admin.css` | Estilos do painel administrativo |
| `frontend/estilos/confirmar-reciclagem.css` | Estilos da tela de confirmação |
| `frontend/theme.js` | Alternância entre tema claro e escuro |
| `backend/rotas/recycling.py` | Geração, consulta e confirmação das entregas por QR Code |
| `backend/database/migrations/001_create_recycling_qr_pending.sql` | Criação da tabela de entregas pendentes |
| `backend/requirements.txt` | Dependências necessárias, incluindo geração de QR Code |

Também houve ajustes nas telas de login, nos estilos compartilhados e na página principal para integrar os novos recursos.

## Rotas utilizadas no fluxo

- `POST /recycling/qr`: cria uma entrega pendente e retorna a imagem do QR Code e o link de confirmação. Uso restrito a administradores.
- `GET /recycling/qr/{token}`: consulta os dados da entrega. Uso restrito a alunos.
- `POST /recycling/qr/{token}/confirm`: confirma a entrega e credita os pontos. Uso restrito a alunos.
- `POST /recycling/recycle`: o registro direto foi desativado e retorna HTTP 410, orientando o uso do QR Code.

## Configuração

O backend usa a variável `FRONTEND_BASE_URL` para montar o endereço que será colocado no QR Code. Se ela não estiver definida, o código usa `http://localhost:5500`, adequado apenas para desenvolvimento local.

A variável `ECOHORA_DB_PATH` permite indicar o caminho do banco SQLite. Sem ela, é usado o banco `backend/database/ecohora.db`.

A migration `001_create_recycling_qr_pending.sql` precisa estar aplicada no banco para que o fluxo de QR Code funcione.

## Observações sobre o escopo

- O painel já consulta dados existentes da API, mas não implementa todos os módulos administrativos previstos no projeto.
- A conversão automática de pontos em horas complementares ainda não faz parte do sistema implementado.
- O fluxo de QR Code registra a entrega e credita os pontos; ele não representa, por si só, a validação de horas complementares pela instituição.
