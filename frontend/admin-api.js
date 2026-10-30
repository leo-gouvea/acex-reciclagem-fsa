// Chamadas do painel administrativo. Carregue depois de api.js: o apiRequest
// de lá já cuida da URL base, dos cookies e dos erros.
// Só rotas que existem hoje no backend; a autorização é feita por ele, não aqui.
// Objeto próprio (e não funções globais) para não colidir com o que outras
// branches adicionarem em api.js.
const AdminApi = {
    // { authenticated, user: { id, name, ra, role } }
    getSession: () => apiRequest("/user/session"),

    // [{ id, material_name, points_per_kilogram }]
    getMaterials: () => apiRequest("/recycling/materials-info"),

    // top 10 por pontos: [{ id, name, ra, points }]
    getRanking: () => apiRequest("/user/ranking"),

    // perfil completo por RA (inclui course e user_class); administrador pode ver qualquer um
    getUser: (ra) => apiRequest(`/user/get/${encodeURIComponent(ra)}`),

    logout: () => apiRequest("/user/logout", { method: "POST" })
};
