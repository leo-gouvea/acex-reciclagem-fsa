# Autenticação, Sessão e Logout — EcoHora

## 1. Objetivo

Foi implementado o controle de sessão do usuário no frontend do EcoHora, integrado à API do backend.

A implementação permite:

* verificar se o usuário possui uma sessão válida;
* impedir o acesso à página principal sem autenticação;
* realizar logout;
* remover a sessão autenticada no backend;
* impedir que uma página protegida seja restaurada pelo histórico do navegador após o logout.

---

## 2. Funcionamento da autenticação

O login é realizado através da API:

```text
POST /user/login
```

Após o login bem-sucedido, o backend cria um cookie HTTP chamado:

```text
access_token
```

Esse cookie é utilizado pelo backend para identificar o usuário nas requisições autenticadas.

O frontend não armazena o token JWT diretamente.

As requisições da API utilizam:

```javascript
credentials: "include"
```

permitindo que o navegador envie o cookie de autenticação para a API.

---

## 3. Verificação da sessão

Foi criado no backend o endpoint:

```text
GET /user/session
```

Esse endpoint utiliza o mesmo mecanismo de autenticação das demais rotas protegidas.

No frontend, a função:

```javascript
checkSession()
```

realiza a chamada para esse endpoint.

A função `getSession()` presente em `auth.js` utiliza `checkSession()` para disponibilizar a verificação de sessão para as páginas da aplicação.

### Fluxo

```text
index.html
    ↓
protectPage()
    ↓
getSession()
    ↓
GET /user/session
    ↓
Backend verifica access_token
    ↓
┌─────────────────────┐
│ Sessão válida?      │
├──────────┬──────────┤
│   SIM    │   NÃO    │
│          │          │
│ continua │ login.html
│ na página │          │
└──────────┴──────────┘
```

Caso a sessão seja inválida, o usuário é redirecionado para:

```text
login.html
```

O redirecionamento utiliza:

```javascript
window.location.replace("login.html");
```

---

## 4. Proteção da página principal

A página `index.html` executa a função:

```javascript
async function protectPage() {
    try {
        await getSession();
        console.log("Sessão válida.");
    } catch (error) {
        console.warn("Sessão inválida:", error.message);
        window.location.replace("login.html");
    }
}
```

Essa verificação é executada quando a página é carregada.

Dessa forma, mesmo que o usuário tente acessar diretamente:

```text
index.html
```

sem possuir uma sessão válida, o acesso à página é bloqueado e o usuário é enviado para a tela de login.

---

## 5. Logout

Foi criado no backend o endpoint:

```text
POST /user/logout
```

O endpoint remove o cookie:

```text
access_token
```

utilizando as mesmas configurações utilizadas na criação do cookie de autenticação.

No frontend, a função:

```javascript
logoutUser()
```

realiza a chamada para o backend.

A função `logout()` em `auth.js` disponibiliza essa operação para a aplicação.

---

## 6. Botão "Sair"

Foi adicionado ao cabeçalho da página principal:

```html
<button id="logoutButton" type="button">Sair</button>
```

Ao clicar no botão:

1. o botão é temporariamente desabilitado;
2. seu texto muda para `Saindo...`;
3. o frontend solicita o logout ao backend;
4. o cookie de autenticação é removido pelo backend;
5. o armazenamento local relacionado ao usuário é limpo;
6. o usuário é redirecionado para `login.html`.

O redirecionamento utiliza:

```javascript
window.location.replace("login.html");
```

---

## 7. Tratamento do histórico do navegador

Após o logout, o usuário pode tentar utilizar os botões **Voltar** e **Avançar** do navegador.

Para evitar que uma versão anteriormente carregada da página protegida seja exibida através do cache de navegação do navegador, foi adicionada uma verificação no evento:

```javascript
pageshow
```

A implementação verifica:

```javascript
event.persisted
```

Quando a página é restaurada pelo histórico/cache do navegador, a sessão é validada novamente.

Caso o usuário não esteja mais autenticado, ele é redirecionado para `login.html`.

Isso evita depender de manipulações artificiais do histórico do navegador.

---

## 8. Arquivos modificados

### `api.js`

Foram adicionadas as funções:

```javascript
checkSession()
logoutUser()
```

Também é mantido:

```javascript
credentials: "include"
```

nas requisições à API.

---

### `auth.js`

Foram adicionadas:

```javascript
getSession()
logout()
```

Essas funções funcionam como camada de acesso às operações de sessão utilizadas pela aplicação.

---

### `index.html`

Foram adicionados:

* botão de logout;
* função `protectPage()`;
* verificação da sessão ao carregar a página;
* função de logout;
* limpeza do armazenamento local;
* redirecionamento após logout;
* tratamento do evento `pageshow`.

---

### `estilos/slide.css`

Foi adicionado o estilo específico para o botão `#logoutButton`, incluindo:

* borda de ação destrutiva;
* estado de hover;
* estado desabilitado;
* integração visual com as variáveis existentes do projeto.

---

## 9. Backend

No backend foram adicionados ao `main.py`:

```text
GET /user/session
POST /user/logout
```

O endpoint `/user/session` utiliza a dependência de autenticação já existente:

```python
check_access
```

Assim, a verificação de sessão segue o mecanismo de autenticação já utilizado pelas demais rotas da API.

O endpoint `/user/logout` remove o cookie `access_token`.

---

## 10. Segurança

O token JWT não é armazenado diretamente no `localStorage`.

A autenticação utiliza o cookie:

```text
access_token
```

configurado pelo backend como:

```text
HttpOnly
Secure
SameSite=None
```

O frontend não precisa acessar diretamente o conteúdo do token.

O `localStorage` utilizado pela aplicação contém apenas o e-mail previamente salvo pela tela de login e não é utilizado como mecanismo de autenticação.

---

## 11. Testes realizados

A implementação foi testada após o deploy da versão atualizada do backend.

### Login

**Resultado:** aprovado.

O usuário realiza o login e é direcionado para `index.html`.

### Validação da sessão

**Resultado:** aprovado.

A página principal consegue validar a sessão através de:

```text
GET /user/session
```

### Acesso direto sem login

**Resultado:** aprovado.

Ao tentar acessar `index.html` sem uma sessão válida, o usuário é redirecionado para `login.html`.

### Logout

**Resultado:** aprovado.

O botão `Sair` encerra a sessão e redireciona o usuário para a tela de login.

### Botão Voltar após logout

**Resultado:** aprovado.

Após realizar logout, utilizar o histórico do navegador não permite recuperar uma sessão válida na página protegida.

### Acesso direto após logout

**Resultado:** aprovado.

Mesmo tentando abrir `index.html` diretamente após o logout, a página verifica a sessão e redireciona para `login.html`.

---

## 12. Fluxo completo

```text
                    ┌──────────────┐
                    │  login.html  │
                    └──────┬───────┘
                           │
                           │ POST /user/login
                           ▼
                    ┌──────────────┐
                    │    Backend   │
                    └──────┬───────┘
                           │
                           │ cria access_token
                           ▼
                    ┌──────────────┐
                    │  index.html  │
                    └──────┬───────┘
                           │
                           │ GET /user/session
                           ▼
                    ┌──────────────┐
                    │ Sessão válida│
                    └──────┬───────┘
                           │
                           │
                    ┌──────▼───────┐
                    │ Usuário usa  │
                    │  aplicação   │
                    └──────┬───────┘
                           │
                           │ clicar "Sair"
                           ▼
                    ┌──────────────┐
                    │ POST /logout │
                    └──────┬───────┘
                           │
                           │ remove access_token
                           ▼
                    ┌──────────────┐
                    │  login.html  │
                    └──────────────┘
```

---

## 13. Estado atual

A implementação de autenticação, validação de sessão e logout está funcional e foi validada utilizando o backend hospedado na Discloud.

A funcionalidade está pronta para ser integrada ao restante do desenvolvimento do EcoHora.
