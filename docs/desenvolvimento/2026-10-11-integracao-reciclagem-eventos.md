# Integração do EcoHora — Reciclagem, Pontuação, Eventos e Grupos

**Data de referência:** 11 de outubro de 2026
**Branch de trabalho:** `feat/integracao-consolidada`
**Objetivo:** registrar a evolução da integração entre frontend e API, os ajustes recentes de interface e as verificações realizadas.

## 1. Contexto

Esta etapa reúne alterações desenvolvidas em diferentes commits e branches do projeto EcoHora ACEX. O histórico inclui integração de reciclagem, cálculo de pontos, eventos, grupos e ranking, sincronização dos dados do dashboard e ajustes de interface.

A branch de integração deve ser revisada como um conjunto antes de ser incorporada à `main`. Os commits anteriores pertencem ao histórico compartilhado do projeto; este documento não atribui individualmente todas as mudanças a uma única pessoa.

## 2. Histórico de integração

Entre os commits presentes no histórico da branch estão:

- `0a602b5` — integração do registro de reciclagem com a API.
- `d18c68e` — integração de eventos e grupos no frontend.
- `e8d4627` — sincronização da pontuação acumulada no dashboard.
- `301b65b` — adição de rotas relacionadas ao ranking e ao gerenciamento de grupos de eventos.
- `db40d6f` — correções adicionais no frontend.

O histórico também contém alterações anteriores nas rotas de reciclagem, no modelo de pontuação, nas validações de usuários e na estrutura de eventos e grupos.

Esses identificadores registram pontos relevantes do histórico, mas não substituem a revisão do diff completo do pull request.

## 3. Registro de reciclagem

O frontend utiliza as funções da camada de API para consultar os materiais disponíveis e registrar uma entrega.

Fluxo geral:

1. Consultar os materiais disponibilizados pela API.
2. Exibir os materiais e suas informações de pontuação.
3. Selecionar o material reciclável.
4. Informar o peso da entrega.
5. Enviar o identificador do material e o peso à API.
6. Atualizar a pontuação apresentada no dashboard após uma resposta válida.

A integração utiliza as funções `getMaterials()` e `registerRecycling()` de `frontend/api.js`.

O registro envia os campos:

- `fk_cd_material`: identificador do material.
- `nr_weight_kilograms`: peso informado em quilogramas.

O frontend espera que a resposta contenha `points_earned` e `total_points`, utilizados para apresentar a pontuação recebida e atualizar o total exibido.

## 4. Formulário de reciclagem

A interface da página Lixão foi ajustada para permitir o registro diretamente na página, sem depender de uma caixa de diálogo `prompt()` do navegador.

O formulário inclui:

- Seletor de material carregado a partir dos dados da API.
- Campo para informar o peso da entrega.
- Mensagens de validação, sucesso e erro na própria página.
- Indicação visual do estado de registro, incluindo desativação temporária do botão durante o envio.
- Aceitação de valores decimais com vírgula ou ponto.

### Regra de peso

A interface valida pesos entre **1 kg e 10 kg**, inclusive.

Esse limite corresponde à validação do formulário no frontend. Para que a mesma regra seja obrigatória em todas as situações, o backend também deve validá-la, pois requisições diretas à API podem ignorar as restrições da interface.

A regra de pontuação por quilograma e o peso mínimo de 1 kg são conceitos diferentes: o mínimo é uma regra de validação definida para o fluxo do projeto.

## 5. Seleção visual dos materiais

Os cartões de Plástico, Papel, Vidro e Metal funcionam como atalhos para a seleção do material no formulário.

O cartão selecionado e o seletor do formulário são sincronizados. A interface utiliza as cores definidas nos estilos dos cartões para destacar o material correspondente.

Os estilos estão distribuídos entre:

- `frontend/estilos/tokens.css`: tokens e padrões gerais dos campos.
- `frontend/estilos/dashboard.css`: aparência dos cartões, formulário e estados selecionados.
- `frontend/index.html`: estrutura da interface e lógica de sincronização.

Foi corrigida a normalização do nome do material para que Plástico seja reconhecido corretamente pela classe CSS `plastico`, sem acento.

## 6. Eventos, grupos e ranking

O histórico da branch contém alterações de integração do frontend com eventos e grupos, além de rotas de gerenciamento e ranking.

Arquivos relevantes incluem:

- `backend/rotas/events.py`
- `frontend/api.js`
- `frontend/index.html`

As funcionalidades devem ser revisadas em conjunto com os contratos da API, as regras de autenticação e os modelos de dados utilizados pelo backend.

Antes do merge, recomenda-se validar a listagem de eventos, a apresentação dos grupos, as operações de gerenciamento e o ranking com dados compatíveis com o ambiente de teste.

Este documento não declara esses fluxos integralmente testados na sessão de 11/10/2026; eles fazem parte do escopo de integração a revisar.

## 7. Pontuação e dashboard

A branch inclui um commit específico para sincronizar a pontuação acumulada no dashboard após o registro de reciclagem.

O fluxo do frontend depende dos valores retornados pela API. Por isso, alterações no cálculo, na resposta ou no armazenamento da pontuação devem ser revisadas conjuntamente entre frontend e backend.

Também é importante verificar o comportamento ao registrar entregas sucessivas e ao receber erros da API, evitando apresentar totais desatualizados ou resultados duplicados.

## 8. Testes e verificações realizados

### Verificações confirmadas

Durante o trabalho de 11/10/2026:

- `git diff --check` foi executado sem apontar erros de whitespace.
- O formulário inline de reciclagem foi conferido no navegador pelo responsável pelo desenvolvimento.
- O registro de reciclagem foi confirmado como funcional.
- O campo de peso e a seleção de materiais foram conferidos.
- O destaque visual foi testado para os quatro materiais.
- A identificação visual de Plástico precisou de uma correção adicional e foi conferida após o ajuste.

### Verificações pendentes para a revisão da integração

Antes do merge, recomenda-se:

- Executar os testes automatizados disponíveis.
- Validar os fluxos de eventos, grupos e ranking.
- Confirmar os contratos das rotas no ambiente utilizado pelo grupo.
- Testar erros de autenticação, respostas inesperadas e falhas de rede.
- Confirmar que o backend rejeita pesos fora do intervalo definido.
- Revisar o diff completo em relação à `main`.
- Confirmar que arquivos auxiliares locais não foram incluídos no pull request.

A existência de arquivos de teste no repositório não significa que eles tenham sido executados nesta etapa.

## 9. Arquivos relevantes

- `frontend/index.html`
- `frontend/api.js`
- `frontend/estilos/dashboard.css`
- `frontend/estilos/tokens.css`
- `backend/rotas/recycling.py`
- `backend/rotas/events.py`
- `backend/rotas/users_operations_improved.py`

A lista identifica arquivos relevantes para a revisão; não significa que todos tenham sido modificados na última etapa.

## 10. Cuidados para a consolidação

A branch `feat/integracao-consolidada` contém commits anteriores à alteração recente do formulário. Por isso, a revisão deve considerar todos os commits que ainda não estão na `main`, além das alterações locais pendentes.

Antes de criar commits:

1. Conferir o diff da branch em relação a `origin/main`.
2. Revisar as alterações locais de `frontend/index.html` e `frontend/estilos/dashboard.css`.
3. Adicionar somente arquivos pertencentes à entrega.
4. Manter backups e arquivos acidentais fora do controle de versão.
5. Executar `git diff --cached --check` e revisar `git diff --cached`.
6. Publicar a branch e abrir um pull request para revisão.

O merge na `main` deve ocorrer após a revisão do grupo e a resolução dos problemas encontrados.

## 11. Continuidade do desenvolvimento

Para os próximos integrantes, recomenda-se:

- Utilizar a branch de integração revisada como referência, após a publicação do pull request.
- Conferir o contrato da API antes de alterar o formato das requisições ou respostas.
- Manter as regras de validação consistentes entre frontend e backend.
- Registrar novos testes e mudanças relevantes nesta documentação ou em documentos específicos.
- Evitar incluir arquivos de backup, configurações locais e artefatos de depuração em commits de funcionalidade.
