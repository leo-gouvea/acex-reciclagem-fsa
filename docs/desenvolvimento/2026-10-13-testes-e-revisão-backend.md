# Integração do EcoHora — Testes Automatizados e Revisão de Regras de Negócio do Backend

**Data de referência:** 13 de outubro de 2026
**Branch de trabalho:** `feat/testes-automacao-backend`
**Commit:** `feat: Adiciona script de testes automáticos para Backend e revisa regras de negócios citados na PR #19`
**Objetivo:** Registrar a implementação da suíte de testes automatizados, as adequações de segurança do banco de dados e a revisão dos contratos de API mencionados pelo Frontend.

## 1. Contexto

Em resposta aos apontamentos levantados na PR #19 (referentes à integração de reciclagem, eventos e validações), esta etapa focou em garantir a estabilidade e a segurança da API do projeto EcoHora ACEX. 

O escopo inclui a criação de um ambiente seguro para testes, a validação rigorosa das regras de pesagem no backend e a modernização de sintaxes descontinuadas detectadas por nossas bibliotecas base.

## 2. Histórico e Resolução de Avisos (PR #19)

As seguintes ações foram tomadas no Backend para contemplar as verificações pendentes levantadas pelo time de Frontend:

- **Trava de Segurança de Peso (`recycling.py`):** Foi removida uma validação redundante e falha na rota `/recycle`. A regra de negócio de pesos entre 1kg e 10kg agora é tratada exclusivamente pelo schema do Pydantic (`PostRecyclingRequest` usando `ge=1, le=10`). Isso garante o bloqueio imediato (Erro 422 - Unprocessable Entity) de requisições maliciosas.
- **Contrato de API Mantido:** Foi comprovado via testes que a rota `/recycle` retorna as chaves `points_earned` e `total_points` exatamente como o Frontend espera, respeitando o contrato de integração.
- **Resolução de Deprecation Warnings (`events.py`):** A sintaxe de documentação dos Schemas foi atualizada de `example` (descontinuado no Pydantic V2) para `examples=["..."]`, modernizando o código e preparando a API para o Pydantic V3.
- **Atualização do Motor de Testes:** A biblioteca de suporte do cliente de testes foi atualizada do obsoleto `httpx` para o `httpx2`, conforme exigido pelas novas versões do FastAPI.

## 3. Ambiente Isolado de Testes Automáticos

Para garantir a qualidade contínua do código sem poluir o banco de dados oficial (`ecohora.db`), foi introduzido um script de testes automatizados utilizando `pytest`.

### Estrutura e Mecanismo de Isolamento
O arquivo principal de testes (`automated_tests.py`) utiliza o recurso de *Fixtures* e *Monkeypatch* do pytest.

Fluxo do "Mordomo" (Isolamento de Banco):
1. Antes de cada teste individual, o sistema utiliza a biblioteca nativa `shutil` para clonar o banco de dados de produção, gerando um arquivo temporário `test_ecohora.db`.
2. A API é forçada a redirecionar todas as suas operações de leitura e escrita para este clone temporário.
3. O teste simula um usuário logado interceptando a dependência `check_access`.
4. Ao final da verificação (independente de sucesso ou falha), o arquivo clone é automaticamente deletado (`os.remove`), mantendo o ambiente limpo.

## 4. Testes e Verificações Realizados

Os seguintes cenários agora estão cobertos automaticamente e foram validados com 100% de sucesso (PASSED) no dia 13/10/2026:

1. **`test_contrato_api_reciclagem`:** Simula um envio válido de 10kg, valida se a API retorna o status 201 (Created) e confere se a resposta JSON possui exatamente as nomenclaturas exigidas pelo Frontend.
2. **`test_bloqueio_peso_acima_do_limite`:** Envia um peso de 15kg e valida se a API intercepta e recusa o pacote com status HTTP 422.
3. **`test_bloqueio_peso_abaixo_do_limite`:** Envia um peso de 0.5kg e valida a mesma recusa.

## 5. Arquivos Modificados/Criados

- `backend/rotas/recycling.py` (Remoção da validação manual do if)
- `backend/rotas/events.py` (Atualização de example para examples)
- `backend/automations/automated_tests.py` (Novo arquivo com a suíte de testes)

## 6. Continuidade do Desenvolvimento

Para os próximos passos e próximos desenvolvedores que aturem no Backend:

- **Sempre execute os testes:** Antes de realizar qualquer *commit* na main, execute `pytest automations/automated_tests.py -v` na raiz do backend.
- **Expandir Cobertura:** Recomenda-se adicionar novos testes automatizados para as rotas de Eventos e Competições em um arquivo separado (ex: `test_eventos.py`), aproveitando a mesma fixture de isolamento de banco de dados.
- **Atenção aos IDs de Teste:** O usuário "mockado" na função `usuario_falso_logado()` deve obrigatoriamente referenciar um `id` que já exista no banco de dados clonado, caso contrário, erros de *Foreign Key* ocorrerão.