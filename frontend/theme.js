/* =========================================================
   EcoHora — tema claro/escuro
   Carregue no <head>, sem defer: aplica o tema antes da primeira
   pintura (evita piscar). A escolha fica em localStorage; sem
   escolha, vale a preferência do sistema (padrão: escuro).
   O botão é criado aqui para não repetir markup em cada página.
========================================================= */
(function () {
  var KEY = "ecohora-theme";
  var root = document.documentElement;
  var COR_BARRA = { dark: "#061815", light: "#f2f7f4" };

  function salvo() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function aplicar(tema) {
    root.setAttribute("data-theme", tema);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", COR_BARRA[tema]);
  }

  var inicial = salvo();
  if (inicial !== "light" && inicial !== "dark") {
    inicial = window.matchMedia && matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }
  aplicar(inicial);

  var SOL = '<svg class="ic-sol" width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="3.6" stroke="currentColor" stroke-width="1.6"/><path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.3 4.3l1.4 1.4M14.3 14.3l1.4 1.4M4.3 15.7l1.4-1.4M14.3 5.7l1.4-1.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';
  var LUA = '<svg class="ic-lua" width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M16.5 11.6A6.8 6.8 0 0 1 8.4 3.5a6.8 6.8 0 1 0 8.1 8.1Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>';

  document.addEventListener("DOMContentLoaded", function () {
    var botao = document.createElement("button");
    botao.type = "button";
    botao.className = "theme-toggle";
    botao.innerHTML = SOL + LUA;

    function rotular() {
      var claro = root.getAttribute("data-theme") === "light";
      botao.setAttribute("aria-label", claro ? "Mudar para tema escuro" : "Mudar para tema claro");
      botao.setAttribute("title", claro ? "Tema escuro" : "Tema claro");
    }
    rotular();

    botao.addEventListener("click", function () {
      var novo = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      aplicar(novo);
      try { localStorage.setItem(KEY, novo); } catch (e) { /* modo privado: vale só nesta visita */ }
      rotular();
    });

    // Cabeçalhos: antes do "Sair" (painel/admin) ou do menu hambúrguer (home).
    // Sem cabeçalho (login): canto superior direito.
    var alvo = document.getElementById("logoutButton") || document.getElementById("menuToggle");
    if (alvo) {
      alvo.parentNode.insertBefore(botao, alvo);
    } else {
      botao.classList.add("theme-toggle-float");
      document.body.appendChild(botao);
    }
  });
})();
