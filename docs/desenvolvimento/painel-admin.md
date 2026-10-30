# Painel administrativo (frontend) — v1

Branch: `feat/dashboard-admin` (a partir de `feat/dashboard-mvp`).
Referência: casos de uso v4 (UC11–UC17, RF17, RF25–RF28, RN06) e cronograma, Sprint 8 (Administração).

## O que existe

Arquivos novos, nada existente foi alterado:

| Arquivo | Função |
|---|---|
| `frontend/admin.html` | Estrutura, ícones (sprite SVG), tela de acesso |
| `frontend/admin.js` | Guarda de acesso, rotas por `#hash`, renderização |
| `frontend/admin-api.js` | Objeto `AdminApi`, só chama rotas que já existem |
| `frontend/estilos/admin.css` | Estilo (prefixo `.adm-`), usa `tokens.css` |
| `frontend/assets/campus-casarao.jpg` | Foto de fundo (confirmar direito de uso) |

Não alterados: `index.html`, `dashboard.css`, `login.js`, `api.js`, `backend/`.
`dashboard.css` não é carregado de propósito (fixa slider e `overflow:hidden` no body).

### Telas com dados reais
- **Visão geral**: nº de materiais, faixa de pontos por kg, líder, barras de pontos/kg, top 5.
- **Materiais**: tabela com pontos por kg.
- **Ranking**: tabela rolável com #, nome, RA, curso, turma, pontos (cabeçalho fixo).

### Telas "aguardando backend" (só mostram o que falta, sem funcionar)
Usuários (UC12·RF26), Pontos de coleta (UC11·RF25), Entregas e auditoria (UC14·UC16·RF27·RF28),
Regras de conversão (UC15·RN06), Relatórios (UC13·RF17).

## Acesso e segurança
- O front lê `role` de `GET /user/session`; só `"Administrador"` entra. **Isso é só UX.**
- A autorização real é do backend (`user.get("role") != "Administrador"` nas rotas admin).
- Sem `innerHTML`: tudo da API entra como texto (testado com `<img onerror>`).
- Erro 401 "Acesso negado" volta ao login; falha parcial mostra "—" e avisa.

## Rotas usadas (todas já existem)
`GET /user/session`, `GET /recycling/materials-info`, `GET /user/ranking`,
`GET /user/get/{ra}`, `POST /user/logout`.

## O que o backend precisa (para Diego)
1. **`/user/ranking` deve devolver `course` e `user_class`.** Hoje devolve só `{id,name,ra,points}`;
   o painel faz 1 chamada `/user/get/{ra}` por linha (shortcut em `admin.js`, ok para 10 linhas, não escala).
   Quando existir, remover o `loadData` de detalhe.
2. **Ranking paginado/completo para admin.** Hoje é top 10 fixo; a tabela já rola e suporta mais linhas.
3. **Rotas dos módulos pendentes** (a definir com o grupo, não inventadas aqui):
   usuários (listar/criar/editar/desativar), pontos de coleta, entregas e auditoria, regras de conversão, relatórios.
4. **Métricas da visão geral** (Seção 10 dos casos de uso): usuários ativos, volume reciclado, entregas, horas resgatadas.

## Problemas de backend encontrados (não corrigidos, fora do escopo)
- `POST /user/register` aceita `user_type` 1–3 publicamente → qualquer um vira administrador.
- `POST /contests/event/group` e `DELETE /contests/event/group/{id}` sem autenticação.
- Rotas admin de reciclagem devolvem 401 em vez de 403 para quem não é admin.
- `/user/ranking` expõe o RA de todos a qualquer usuário logado.

## Como testar
Conta de teste com `user_types.nm_type = "Administrador"` (peça ao Diego para promover).
Abrir `frontend/admin.html` servido por HTTP (a API usa cookie `samesite=none; secure`).
Conta de aluno vê "Área restrita".

## Para completar depois
- Módulos pendentes acima, conforme as rotas forem criadas.
- Opcional: busca/filtro nas tabelas, coluna do nome fixa no celular.
