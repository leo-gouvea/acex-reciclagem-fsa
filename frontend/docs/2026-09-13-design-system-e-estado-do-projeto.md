# EcoHora — Design System e Estado do Projeto

**Data**: 13 de Setembro de 2026
**Branch de origem sugerida**: `new-homepage` (a partir de `https://github.com/leo-gouvea/acex-reciclagem-fsa`)
**Substitui**: `2026-09-12-redesign-homepage.md` e `2026-09-12-redesign-homepage-parte-2.md` — este arquivo é a versão definitiva e consolidada. Os dois anteriores podem ficar no repositório como histórico, mas a partir de agora **este é o documento de referência**.

---

## Como usar este documento

Se você é um Claude (ou outra IA) continuando este projeto numa conversa nova: leia a Parte 1 antes de tocar em qualquer arquivo. É o contrato visual do site — quebrar ele é o tipo de coisa que o projeto já teve que corrigir várias vezes (ver Parte 3, "erros que já se repetiram").

Se você é o Leonardo abrindo isso depois de um tempo: a Parte 2 é o changelog completo até agora; a Parte 4 é a única coisa que precisa de ação antes de qualquer deploy real.

---

# Parte 1 — Design System

## 1.1 Arquivo-fonte

Tudo abaixo vive em `frontend/estilos/tokens.css`. Toda página do site importa esse arquivo **primeiro**, antes de qualquer CSS específico de página (`home.css`, `login.css`, `dashboard.css`).

## 1.2 Cores

```css
:root {
  --bg: #071f1c;              /* fundo principal, verde quase preto */
  --bg-alt: #0b2b23;          /* fundo alternativo, um pouco mais claro */
  --surface: #0e332a;         /* superfície de cards */
  --card: #103832;            /* cards mais escuros (login) */

  --green: #29c777;           /* marca */
  --green-light: #7be3a8;     /* hover / acento claro */
  --green-deep: #0f3a2c;      /* base de gradiente/vinheta */

  --warm: #ff9142;            /* acento quente — ação/embalagem */
  --gold: #ffcf5c;            /* segundo acento — usado sobre foto */
  --blue: #65b9ff;            /* acento de navegação/utilidade — da paleta ORIGINAL do Diego, não inventado */
  --danger: #ff6b6b;          /* avisos, ação destrutiva (logout) */

  --text: #f4fff9;
  --muted: #a9c4bb;
  --muted-dark: #7f9c92;
  --placeholder: #6d9185;

  --font-hand: "Kalam", "Comic Sans MS", cursive;
}
```

**Regra de uso das cores**: verde é a marca (CTAs primários, ícones de "isso é bom"), laranja é ação/embalagem, dourado é o segundo acento (usado sobre foto, onde o verde some), azul é só navegação/utilidade (`Conhecer o projeto`, `Voltar ao topo`) — **nunca** nos CTAs de conversão principais. Vermelho só para logout/exclusão.

## 1.3 Tipografia

Duas fontes, com papel bem definido:

| Fonte | Onde usar | Onde NÃO usar |
|---|---|---|
| **Manrope** (`--`, padrão do `body`) | Título (`h1`), subtítulo do hero, todo `h2`/`h3`, botões, navegação, formulários | — |
| **Kalam** (`var(--font-hand)`, classe `.text-hand`) | Parágrafo de apoio (`<p>`) dentro do conteúdo — legendas de passo, descrição de benefício, texto de anotação | Título, subtítulo, `h1`/`h2`/`h3`, botões, navegação |

A regra é simples: **se é um heading, é Manrope. Se é o texto corrido por baixo do heading, é `.text-hand`.** Essa divisão existe pra imitar o efeito de "nota de caderno" que já é a identidade da marca (o próprio "seu caderno vale horas"), sem transformar a página inteira num quadro-negro — títulos continuam limpos e "de app", só o texto de apoio ganha esse calor.

Nunca usar Inter/Roboto/Arial/Helvetica.

## 1.4 Botões

Todos partem da classe base `.btn` (pill, `border-radius: var(--radius-pill)`, padding e transição padrão). Variantes, por ordem de "quanto peso visual":

| Classe | Aparência | Uso |
|---|---|---|
| `.btn-cta-glow` | Fundo escuro (`--bg-alt`), **sem preenchimento colorido** — só uma borda fina com anel giratório verde→dourado→laranja→verde-claro | CTA de conversão de verdade: "Comece a ganhar" (hero), "Entrar"/"Criar perfil" (login), "Quero participar" (CTA de fechamento). **É sempre a mesma classe** nos três lugares — não criar uma variante nova por página. |
| `.btn-primary` | Preenchimento sólido dourado | Reservada, mas hoje nenhum botão a usa sozinha (todo CTA "primário de verdade" virou `.btn-cta-glow`) |
| `.btn-solid-green` | Preenchimento sólido verde | Ações dentro do painel (ex: "Registrar reciclagem") |
| `.btn-nav` | Borda verde, transparente | Ação primária da navbar ("Entrar no site") |
| `.btn-nav-outline` | Borda azul, transparente | Ação secundária da navbar ("Conhecer o projeto") |
| `.btn-outline` | Borda laranja, transparente | Ações secundárias fora da navbar |
| `.btn-ghost` | Sem borda visível, só texto | Ações terciárias, menu mobile |
| `.btn-danger-outline` | Borda vermelha | Logout |

### A borda giratória (`.btn-cta-glow`), como funciona

```css
@property --cta-angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}

@keyframes cta-border-spin {
  to { --cta-angle: 360deg; }
}
```
Duas camadas (`::before` borrado pro brilho, `::after` nítido pra borda), as duas com `conic-gradient(from var(--cta-angle), var(--green), var(--gold), var(--warm), var(--green-light), var(--green))`, girando em loop de 4.5s. Cor da própria marca — nunca um arco-íris genérico de tutorial. **Não depende de `prefers-reduced-motion`** — decisão consciente, ver Parte 3.

Referência original da técnica (adaptada, não copiada literalmente): https://theosoti.com/blog/animated-gradient-borders/

## 1.5 Ícones

SVG monoline, sempre feito à mão no mesmo estilo (`stroke-width="2"`, `stroke-linecap="round"`, sem preenchimento sólido) — **nunca emoji fazendo de ícone**. Único ícone que é imagem de verdade (não SVG): a marca (`assets/Ca105ad9cfc8580c765101d17bbb2323.webp`, a folha verde — é o asset real que o Diego já usava, não uma SVG recriada).

## 1.6 Anotações "de lousa" (`assets/doodles/`)

Elemento novo do design system, adicionado nesta rodada. Vetores de verdade (não gerados por IA nem desenhados à mão por mim) — vieram prontos do Leonardo.

| Arquivo | Uso |
|---|---|
| `doodle-num-1.png` … `doodle-num-4.png` | Numeral desenhado, substitui número em círculo em listas passo-a-passo (`.how-step-num`) |
| `doodle-underline-long.png` | Sublinhado abaixo de título de seção mais longo (`.doodle-underline`) |
| `doodle-underline-short.png` | Mesma coisa, versão curta (`.doodle-underline.is-short`) |
| `doodle-arrow-swoop.png`, `doodle-arrow-curl.png` | Seta apontando pra um elemento específico, com legenda em `.text-hand` ao lado (`.doodle-note .doodle-arrow` / `.doodle-label`) |

**Regra de moderação, importante**: no máximo **um sublinhado por título de seção** e **uma seta por seção inteira**. Isso é tempero, não papel de parede — a primeira versão dessa ideia (inspirada num mock do Gemini) tinha post-it, fita adesiva e rabisco em tudo quanto é canto, e foi rejeitada por destoar do resto do site, que é limpo e geométrico. Só a numeração, o sublinhado e uma seta pontual sobreviveram ao corte.

Ainda não usados (disponíveis se fizer sentido depois): `assets/folha_*.png` (recortes de folha de caderno rasgada, cores variadas) — foram enviados junto mas não foram integrados ainda.

**Não usado, e não deve ser**: `CTA.png` (um post-it pronto com "Quero começar a participar!" já desenhado na imagem). Texto preso em imagem não é acessível (leitor de tela não lê, não dá pra traduzir/editar a frase depois) — qualquer CTA continua sendo HTML de verdade com `.btn-cta-glow`.

## 1.7 Animação

Convenção do projeto: **animação decorativa de UI (borda de botão, ícone flutuando) não segue `prefers-reduced-motion` na home** — decisão consciente e já documentada (ver Parte 3.2). Isso é uma exceção deliberada; páginas fora da home (o painel, `dashboard.css`) continuam respeitando a preferência normalmente, e é assim que deve continuar a menos que alguém decida mudar os dois lugares junto.

## 1.8 Estrutura de seção da home

Ordem atual, de cima pra baixo:

1. `.hero` — título, subtítulo, palavra digitando, CTA, relógio-folha animado
2. `.intro` (`id="sobre"`) — "Conheça o projeto": só título + um parágrafo curto. Não vira card, não repete conteúdo de seção nenhuma abaixo.
3. `.how` (`id="como-funciona"`) — "Como funciona, em quatro passos": linha do tempo vertical numerada (não é mais grade de 3 cards)
4. `.campus` — foto + texto sobre o dia a dia na FSA
5. `.benefits` — "Por que participar": 3 itens lado a lado, ícone + título + texto, **sem card, sem borda** (era assim antes de qualquer redesign, e continua — é o padrão do resto da página)
6. `.closing-cta` — convite final + `.btn-cta-glow`, sem estatística inventada

Não existe mais (removida por ser 100% duplicada): uma seção "Conheça a iniciativa" com 3 cards bordados repetindo item 2+3+5 acima com emoji no título. Se ela reaparecer em algum merge futuro, é sinal de que alguém restaurou uma versão antiga por engano — apagar de novo.

---

# Parte 2 — Changelog Completo

## 2.1 Identidade visual (rodadas iniciais)
- Reescrita completa do CSS a partir de um scaffold com Arial, `#1f1f1f`, gradiente de painel quebrado e emoji como ícone.
- Criação de `tokens.css` como fonte única de cores/tipografia/componentes.
- Reconstrução de `pages/combate/batalha.html` e `raid.html` (estavam com link morto pra um `estilos/style.css` inexistente, `alt="batata"` no logo, e emoji como stat de personagem).
- Remoção de `estilos/slide.css` e `pages/combate/boss.css` (código morto, nada mais linkava pra eles).

## 2.2 Correções de bugs reais encontrados no caminho
- `--danger` era usado em `.btn-danger-outline` e no badge "VS" da batalha, mas nunca tinha sido definido em `tokens.css` — adicionado.
- `background-position: center, calc(center + 50px)` em `home.css` — CSS inválido (`calc()` não aceita a palavra-chave `center`), a declaração inteira provavelmente era ignorada pelo navegador. Corrigido pra `center calc(50% + 50px)`.
- O centro do ponteiro do relógio-folha (`#clockHand`) apareceu errado **duas vezes** em sessões diferentes (`391, 574` em vez de `454, 612`, medido pixel a pixel no PNG `assets/leaf-clock.png`). Se aparecer errado de novo, o valor certo é `(454, 612)` em coordenadas do `viewBox="0 0 956 1199"`.
- Um comentário em `home.js` dizia que a digitação parava sob "reduzir movimento", mas o código que fazia isso tinha sido apagado numa sessão sem atualizar o comentário — corrigido (ver 2.4).
- `manifest.webmanifest` tinha um `related_applications` apontando pro Play Store do **Moodle Mobile** (resíduo de tutorial) e um "screenshot" com legenda genérica em inglês — os dois removidos. `start_url` trocado de `"."` pra `"./home.html"` (não depender de qual arquivo o servidor serve como padrão).
- `login.js` tinha emoji em texto de toast ("sucesso! 🌱", "sucesso! 🚀") — removidos, consistente com "sem emoji como ícone".
- Ícone da marca (`.brand-mark`) era uma SVG desenhada à mão; trocado por `<img>` com o asset real do Diego (`assets/Ca105ad9cfc8580c765101d17bbb2323.webp`), em `home.html`, `index.html`, `login.html`, `batalha.html` e `raid.html`.

## 2.3 PWA
- `manifest.webmanifest` e `sw.js` existiam no repositório mas não estavam linkados em nenhuma página — conectados em `home.html`, `index.html` e `login.html`.
- `sw.js` recebeu um listener de `fetch` (passthrough, sem cache ainda) — sem isso alguns navegadores nem contam o service worker pro critério de instalação do PWA.

## 2.4 O vaivém do `prefers-reduced-motion` (histórico, pra não repetir)
1. V1: o projeto ignorava a preferência de sistema inteiramente (decisão de outra sessão).
2. V2 (Claude): reintroduzi a checagem em 4 lugares de uma vez (borda do CTA, giro do relógio, flutuar da folha, digitação) — todas as animações pararam ao mesmo tempo pra quem testou num navegador/SO com "reduzir movimento" ligado, parecendo que tudo tinha quebrado.
3. V3 (atual, definitiva): removida de novo, dessa vez documentada como decisão consciente. As animações da home **sempre rodam**. Se precisar mudar isso no futuro, mexer em `tokens.css` (`.btn-cta-glow`) e `home.css` (`#clockHand`, `.leaf-clock-img`, `.leaf-clock-hand-overlay`, `.how-timeline` se ganhar animação) — sempre nos dois arquivos juntos, nunca só um.

## 2.5 Conteúdo da home
- Consolidação: existiam duas versões parcialmente sobrepostas do conteúdo do Diego (texto cru de "Conheça o Projeto / Como Funciona / Por que Participar") — uma nas seções definitivas (`.intro`, `.how`, `.benefits`), outra numa seção extra `.info` com 3 cards e emoji, nunca apagada. A `.info` foi removida.
- `.how` (Como Funciona) passou de grade de 3 cards pra linha do tempo vertical de 4 passos, com numeral desenhado (ver 1.6). Verbos alinhados com o texto original do Diego: Separe / Entregue / Registre / Ganhe.
- `.benefits` (Por que Participar) manteve o formato sem card — item com ícone, título, texto — que era o único trecho da home que já não tinha o problema de inconsistência visual.
- `.closing-cta` criada do zero: convite final antes do rodapé, com `.btn-cta-glow`. Copy escrita sem estatística inventada (o mock de referência sugeria "+500 alunos", que não é um número real do projeto).
- `.intro` ("Conheça o Projeto") recriada — tinha sido perdida entre sessões, restaurada com o mesmo texto de antes, agora com sublinhado desenhado e o parágrafo em `.text-hand`.

## 2.6 Alinhamento com a home do Diego
- `--blue: #65b9ff` resgatado da paleta original dele (existia no `slide.css` antigo, antes do redesign) — usado em `.btn-nav-outline` e `.back-to-top`.
- `.brand-name` ("EcoHora" na navbar) aumentado de `1.25rem`/700 pra `1.55rem`/800.
- Fundo do hero e do login unificados: os dois usam `assets/campus-terciario.png` (antes o login usava uma versão mais antiga/menor, `hero-campus.jpg`).

---

# Parte 3 — Design system anterior, decisões que já foram testadas e revertidas

Registro pra não repetir experimento que já foi feito e descartado:

- **Post-it/fita adesiva/rabisco em todo canto** (inspirado num mockup do Gemini): tentado uma vez, revertido — destoava do resto do site, que é limpo/geométrico. O que sobreviveu foi só a numeração desenhada, o sublinhado e uma seta pontual (ver 1.6).
- **CTA com preenchimento sólido + halo por trás**: era a primeira versão da borda giratória. Trocado pro formato atual (fundo escuro, só a borda colorida) a pedido explícito — "só a borda deve ser colorida e animada".
- **`.btn-primary` + `.btn-cta-glow` juntas na mesma tag**: não fazer mais isso. `.btn-primary` preenche sólido dourado, o que brigava com o fundo escuro que `.btn-cta-glow` precisa. Hoje `.btn-cta-glow` é auto-suficiente (define seu próprio fundo/cor), usar sozinha com `.btn`.

---

# Parte 4 — Ação pendente antes de qualquer deploy real

## 4.1 O atalho de desenvolvimento que pula o login

Em `frontend/index.html`, dentro do bloco `<!-- CONTROLE DE SESSÃO -->`, existe isto:

```javascript
// =========================================================
// ATALHO DE DESENVOLVIMENTO — REMOVER ANTES DE ENTREGAR
// A API só aceita login vindo do domínio publicado, então
// rodando local (file:// ou 127.0.0.1) o login trava. Esse
// atalho pula a checagem de sessão pra dar pra navegar pelas
// telas sem precisar logar.
// Pra tirar: apague a linha DEV_SKIP_LOGIN e o bloco
// "if (DEV_SKIP_LOGIN) return;" logo no começo de protectPage().
const DEV_SKIP_LOGIN = true;
// =========================================================

async function protectPage() {
  if (DEV_SKIP_LOGIN) {
    console.warn('[DEV] Checagem de sessão pulada — não use isso em produção.');
    return;
  }

  try {
    await getSession();
    console.log('Sessão válida.');
  } catch (error) {
    console.warn('Sessão inválida:', error.message);
    window.location.replace('login.html');
  }
}
```

**Isso existe de propósito** — foi pedido numa sessão anterior porque a API só aceita cookie de sessão vindo do domínio publicado, então testar `index.html` localmente (`file://` ou `127.0.0.1`) sempre jogava pro login. Enquanto essa flag for `true`, **qualquer pessoa que abrir `index.html` acessa o painel sem estar logada** — inclusive no domínio publicado, se isso for parar em produção assim.

### Como reativar a trava (obrigatório antes de publicar de verdade)

Duas opções, mesma coisa:

**Opção rápida** — mudar a flag:
```javascript
const DEV_SKIP_LOGIN = false;
```

**Opção limpa** — apagar o atalho inteiro, voltando exatamente pro estado original:
```javascript
async function protectPage() {
  try {
    await getSession();
    console.log('Sessão válida.');
  } catch (error) {
    console.warn('Sessão inválida:', error.message);
    window.location.replace('login.html');
  }
}
```
(ou seja: apagar o bloco `DEV_SKIP_LOGIN` inteiro — a constante e o `if` dentro de `protectPage()` — deixando só o `try/catch` que já chama `getSession()` e redireciona pra `login.html` se a sessão for inválida)

Isso é a única coisa neste documento que é **bloqueante** — o resto é design, isso é segurança de acesso.

## 4.2 Sobre a branch nova

Este pacote assume que a branch `new-homepage` (ou o nome que for escolhido) parte do estado atual do repositório do Diego em `https://github.com/leo-gouvea/acex-reciclagem-fsa`. Os arquivos entregues aqui (zip) têm a mesma estrutura de pastas do repositório — `frontend/`, `frontend/estilos/`, `frontend/assets/`, `frontend/pages/combate/`, `frontend/docs/` — então dá pra copiar por cima direto, sem reorganizar nada. Os únicos arquivos genuinamente novos que não existiam antes são os de `frontend/assets/doodles/` e este próprio documento.
