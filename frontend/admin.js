// Painel administrativo. Depende de api.js e admin-api.js, nessa ordem.
//
// O guard de role abaixo é só UX: esconde uma tela que não serve à conta.
// Qualquer um pode mexer neste JS pelo navegador, então a autorização
// de verdade continua nas rotas do backend.
"use strict";

// Nome do perfil em user_types, o mesmo que as rotas administrativas checam.
const ADMIN_ROLE = "Administrador";

// Módulos dos casos de uso v4 que ainda não têm API. Sem botões: nada aqui
// finge funcionar.
const PENDING = [
    {
        id: "usuarios", label: "Usuários", icon: "users", refs: "UC12 · RF26",
        missing: [
            "Listar e buscar usuários (hoje só existe a consulta por RA exato).",
            "Status da conta (aprovado ou bloqueado): a tabela users não tem esse campo.",
            "Log das ações administrativas."
        ]
    },
    {
        id: "pontos-de-coleta", label: "Pontos de coleta", icon: "pin", refs: "UC11 · RF25",
        missing: [
            "Tabela e rotas de pontos de coleta.",
            "Vínculo entre operadores e pontos."
        ]
    },
    {
        id: "entregas-auditoria", label: "Entregas e auditoria", icon: "box", refs: "UC14 · UC16 · RF27 · RF28",
        missing: [
            "Listagem de todas as entregas (o histórico hoje só vem por usuário).",
            "Status, operador e ponto de coleta na tabela recycling.",
            "Log de eventos e regras antifraude."
        ]
    },
    {
        id: "regras-de-conversao", label: "Regras de conversão", icon: "swap", refs: "UC15 · RN06",
        missing: [
            "Editar pontos por kg (hoje só dá para criar ou excluir material).",
            "Multiplicador de campanha, limite mensal e teto de horas por curso.",
            "Conversão de pontos em horas."
        ]
    },
    {
        id: "relatorios", label: "Relatórios", icon: "report", refs: "UC13 · RF17",
        missing: [
            "Consulta com filtros por período, curso, ponto e material.",
            "Exportação em CSV e PDF."
        ]
    }
];

// Mesmos ícones da aba Lixão; material novo cai no genérico.
const MATERIAL_ICONS = { plastico: "plastico", papel: "papel", vidro: "vidro", metal: "metal" };

const NS = "http://www.w3.org/2000/svg";
const fmt = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });
const $ = (id) => document.getElementById(id);

let loading = false;
const data = { materials: null, ranking: null }; // null = não carregou

// Monta elementos sem innerHTML: o que vem da API entra só como texto.
function h(tag, props = {}, ...children) {
    const el = document.createElement(tag);

    for (const [key, value] of Object.entries(props)) {
        if (key === "class") el.className = value;
        else if (key === "text") el.textContent = value;
        else if (key.startsWith("on")) el.addEventListener(key.slice(2), value);
        else el.setAttribute(key, value);
    }

    el.append(...children.filter(Boolean));
    return el;
}

function icon(name) {
    const svg = document.createElementNS(NS, "svg");
    const use = document.createElementNS(NS, "use");

    svg.setAttribute("class", "adm-icon");
    svg.setAttribute("aria-hidden", "true");
    use.setAttribute("href", `#i-${name}`);
    svg.append(use);
    return svg;
}

const num = (v) => (Number.isFinite(Number(v)) ? Number(v) : 0);
const goToLogin = () => window.location.replace("login.html");

// Sem sessão o backend responde "Acesso negado..." (utils/jwt_validation.py).
// Falha de rede ou 5xx não deve mandar ninguém para o login.
const isAuthError = (e) => /^acesso negado/i.test(e?.message ?? "");
const authFailed = (results) => results.some((r) => r.status === "rejected" && isAuthError(r.reason));

// "Plástico" -> "plastico" para achar o ícone
function materialIcon(name) {
    const key = name.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();
    return icon(MATERIAL_ICONS[key] ?? "box");
}

// ---- acesso -------------------------------------------------------------

function showGate(kind, detail) {
    $("adminApp").hidden = true;
    $("adminGate").hidden = false;

    document.querySelectorAll("[data-gate]").forEach((s) => {
        s.hidden = s.dataset.gate !== kind;
    });

    if (detail !== undefined) $("gateError").textContent = detail;
}

async function initAdmin() {
    showGate("loading");

    let session;

    try {
        session = await AdminApi.getSession();
    } catch (error) {
        if (isAuthError(error)) return goToLogin();
        return showGate("error", error.message);
    }

    if (!session?.authenticated || !session.user) return goToLogin();
    if (session.user.role !== ADMIN_ROLE) return showGate("restricted");

    $("adminUserName").textContent = session.user.name || "Administrador";
    $("adminGate").hidden = true;
    $("adminApp").hidden = false;

    route(false);
    loadData();
}

async function handleLogout() {
    $("logoutButton").disabled = true;

    try {
        await AdminApi.logout();
    } catch (error) {
        console.error("Erro ao sair:", error);
    }

    // Igual ao painel do aluno: sai mesmo que a API falhe.
    try {
        localStorage.removeItem("usuarioEmail");
    } catch {
        // storage indisponível
    }

    goToLogin();
}

// ---- navegação ----------------------------------------------------------

// Os ids das seções têm prefixo "sec-" para não baterem com o hash da URL;
// se batessem, o navegador rolaria a seção para trás do header fixo.
function route(moveFocus) {
    const wanted = $(`sec-${location.hash.slice(1)}`);
    const current = wanted?.matches("[data-section]") ? wanted : $("sec-visao-geral");
    const id = current.id.slice(4);

    document.querySelectorAll("[data-section]").forEach((s) => {
        s.hidden = s !== current;
    });

    document.querySelectorAll(".adm-nav a").forEach((a) => {
        if (a.hash === `#${id}`) a.setAttribute("aria-current", "page");
        else a.removeAttribute("aria-current");
    });

    setDrawer(false);
    const title = current.querySelector("h1");

    $("adminMain").classList.toggle("narrow", current.hasAttribute("data-narrow"));
    $("dataToolbar").hidden = current.dataset.section !== "data";
    document.title = `${title.textContent} · Administração · EcoHora`;

    if (moveFocus) {
        window.scrollTo(0, 0);
        title.focus();
    }
}

function buildPending() {
    for (const m of PENDING) {
        $("navPending").append(
            h("li", {}, h("a", { href: `#${m.id}` }, icon(m.icon), h("span", { class: "adm-nav-text", text: m.label })))
        );

        $("adminMain").append(
            h("section", { id: `sec-${m.id}`, "data-section": "pending", "data-narrow": "", hidden: "", "aria-labelledby": `h-${m.id}` },
                h("h1", { id: `h-${m.id}`, tabindex: "-1", text: m.label }),
                h("p", { class: "adm-note", text: `${m.refs} · aguardando backend` }),
                h("div", { class: "adm-panel" },
                    h("ul", { class: "adm-missing" }, ...m.missing.map((text) => h("li", { text })))
                )
            )
        );
    }
}

// ---- tabela rolável -----------------------------------------------------

const note = (text, retry) =>
    h("p", { class: "adm-note", role: "status" }, text,
        retry && h("button", { class: "adm-link", type: "button", text: "Tentar de novo", onclick: loadData }));

// Planilha: cabeçalho fixo e rolagem dentro da caixa, para aguentar listas grandes.
// columns: [{ label, icon?, num?, head? }]  (head = célula que nomeia a linha)
// rows: lista de listas de células (texto ou elemento)
function sheet(labelledby, columns, rows, wide) {
    const head = columns.map((c) =>
        h("th", { scope: "col", class: c.num ? "num" : "" }, c.icon && icon(c.icon), c.label)
    );

    const body = rows.map((cells) =>
        h("tr", {}, ...cells.map((cell, i) =>
            h(columns[i].head ? "th" : "td", {
                class: columns[i].num ? "num" : "",
                ...(columns[i].head && { scope: "row" })
            }, cell)
        ))
    );

    // tabindex 0: sem ele quem usa só o teclado não consegue rolar a caixa
    return h("div", { class: "adm-sheet", role: "region", tabindex: "0", "aria-labelledby": labelledby },
        h("table", { class: wide ? "adm-table wide" : "adm-table" },
            h("thead", {}, h("tr", {}, ...head)),
            h("tbody", {}, ...body)
        )
    );
}

// ---- telas --------------------------------------------------------------

const figure = (iconName, value, label) =>
    h("div", { class: "adm-panel adm-figure" },
        icon(iconName),
        h("div", {}, h("strong", { text: value }), h("span", { text: label }))
    );

function renderOverview() {
    const { materials, ranking } = data;
    const rates = materials?.map((m) => m.points) ?? [];
    const min = Math.min(...rates);
    const max = Math.max(...rates);
    const leader = ranking?.[0];

    let range = "—";
    if (rates.length) range = min === max ? fmt.format(min) : `${fmt.format(min)} a ${fmt.format(max)}`;

    $("overviewFigures").replaceChildren(
        figure("plastico", materials ? String(materials.length) : "—", "materiais"),
        figure("scale", range, "pontos por kg"),
        figure("star", leader ? `${fmt.format(leader.points)} pts` : "—", leader ? `líder: ${leader.name}` : "líder do ranking")
    );

    // barras: cada material contra o de maior pontuação
    if (!materials) $("overviewBars").replaceChildren(note("Não foi possível carregar os materiais.", true));
    else if (!materials.length) $("overviewBars").replaceChildren(note("Nenhum material cadastrado."));
    else {
        $("overviewBars").replaceChildren(
            h("ul", { class: "adm-bars" }, ...materials.map((m) =>
                h("li", {},
                    materialIcon(m.name),
                    h("span", { class: "adm-bar-name", text: m.name }),
                    h("span", { class: "adm-bar" }, h("i", { style: `width:${max ? (m.points / max) * 100 : 0}%` })),
                    h("span", { class: "adm-value", text: fmt.format(m.points) })
                )
            ))
        );
    }

    if (!ranking) $("overviewTop").replaceChildren(note("Não foi possível carregar o ranking.", true));
    else if (!ranking.length) $("overviewTop").replaceChildren(note("Ainda não há pontuações."));
    else {
        $("overviewTop").replaceChildren(
            h("ol", { class: "adm-top" }, ...ranking.slice(0, 5).map((r, i) =>
                h("li", {},
                    h("span", { class: "adm-pos" }, i === 0 ? icon("star") : String(i + 1)),
                    h("span", { class: "adm-bar-name", text: r.name }),
                    h("span", { class: "adm-value", text: `${fmt.format(r.points)} pts` })
                )
            ))
        );
    }
}

function renderMaterials() {
    const { materials } = data;
    const box = $("materialsBody");

    if (!materials) box.replaceChildren(note("Não foi possível carregar os materiais.", true));
    else if (!materials.length) box.replaceChildren(note("Nenhum material cadastrado."));
    else {
        box.replaceChildren(sheet("h-materiais",
            [{ label: "Material", head: true }, { label: "Pontos por kg", icon: "scale", num: true }],
            materials.map((m) => [
                h("span", { class: "adm-cell-lead" }, materialIcon(m.name), m.name),
                fmt.format(m.points)
            ])
        ));
    }
}

function renderRanking() {
    const { ranking } = data;
    const box = $("rankingBody");

    if (!ranking) box.replaceChildren(note("Não foi possível carregar o ranking.", true));
    else if (!ranking.length) box.replaceChildren(note("Ainda não há pontuações."));
    else {
        box.replaceChildren(sheet("h-ranking",
            [
                { label: "#" },
                { label: "Nome", head: true },
                { label: "RA", icon: "id" },
                { label: "Curso", icon: "cap" },
                { label: "Turma", icon: "users" },
                { label: "Pontos", icon: "star", num: true }
            ],
            ranking.map((r, i) => [
                h("span", { class: "adm-pos" }, i === 0 ? icon("star") : "", String(i + 1)),
                r.name,
                r.ra,
                r.course || "—",
                r.group || "—",
                fmt.format(r.points)
            ]),
            true
        ));
    }
}

// ---- carregamento -------------------------------------------------------

// ok -> lista de itens; resposta fora do formato -> null
const toList = (value, map) => (Array.isArray(value) ? value.map(map) : null);

async function loadData() {
    if (loading) return;
    loading = true;

    $("refreshButton").disabled = true;
    $("lastUpdated").textContent = "Atualizando…";

    const [mat, rank] = await Promise.allSettled([AdminApi.getMaterials(), AdminApi.getRanking()]);

    // Sessão caiu com o painel aberto: volta ao login, como o painel do aluno.
    if (authFailed([mat, rank])) return goToLogin();

    data.materials = toList(mat.value, (m) => ({
        name: String(m?.material_name ?? "Material sem nome"),
        points: num(m?.points_per_kilogram)
    }));
    data.ranking = toList(rank.value, (r) => ({
        name: String(r?.name ?? "Usuário"),
        ra: String(r?.ra ?? "—"),
        points: num(r?.points),
        course: "",
        group: ""
    }));

    let detailFailed = false;

    if (data.ranking) {
        // shortcut: uma chamada por linha (são só 10) porque /user/ranking não traz
        // curso nem turma. Trocar quando o backend incluir esses campos no ranking.
        const details = await Promise.allSettled(data.ranking.map((r) => AdminApi.getUser(r.ra)));

        if (authFailed(details)) return goToLogin();

        details.forEach((d, i) => {
            if (d.status === "fulfilled") {
                data.ranking[i].course = d.value?.course ?? "";
                data.ranking[i].group = d.value?.user_class ?? "";
            } else detailFailed = true;
        });
    }

    renderOverview();
    renderMaterials();
    renderRanking();

    const time = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    const failed = !data.materials || !data.ranking || detailFailed;

    $("lastUpdated").textContent = `Atualizado às ${time}${failed ? ", com falhas" : ""}`;
    $("refreshButton").disabled = false;
    loading = false;
}

// ---- início -------------------------------------------------------------

// Gaveta do menu no celular: mesmo gesto da navegação do painel do aluno.
const drawer = document.querySelector(".adm-sidebar");
const handle = $("navHandle");
let touchY = 0;

function setDrawer(open) {
    drawer.classList.toggle("expanded", open);
    handle.setAttribute("aria-expanded", String(open));
}

handle.addEventListener("click", () => setDrawer(!drawer.classList.contains("expanded")));
drawer.addEventListener("touchstart", (e) => { touchY = e.touches[0].clientY; }, { passive: true });
drawer.addEventListener("touchmove", (e) => {
    const diff = touchY - e.touches[0].clientY;
    if (diff > 15) setDrawer(true);
    else if (diff < -15) setDrawer(false);
}, { passive: true });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") setDrawer(false); });

buildPending();
window.addEventListener("hashchange", () => route(true));
$("refreshButton").addEventListener("click", loadData);
$("logoutButton").addEventListener("click", handleLogout);
$("retryButton").addEventListener("click", initAdmin);

// voltou do cache do navegador (botão "voltar" depois de sair)
window.addEventListener("pageshow", (e) => {
    if (e.persisted) initAdmin();
});

initAdmin();
