const entrarForm = document.getElementById("entrarForm");
const criarContaForm = document.getElementById("criarContaForm");

const loginForm = document.getElementById("loginForm");
const cadastroForm = document.getElementById("cadastroForm");

const message = document.getElementById("message");

/* =========================================================
   REGRAS DE SENHA
   Espelha PATTERN_PASSWORD do backend (users_operations_improved.py):
   só letras sem acento, números e @ $ ! % * ? & _ . — com ao menos
   uma minúscula, uma maiúscula, um número e um símbolo. O limite de
   72 bytes é do bcrypt. A senha nunca é exibida nem registrada.
========================================================= */

const SENHA_REGRAS = [
  { id: "tam",  texto: "De 6 a 72 caracteres", falta: "de 6 a 72 caracteres",
    ok: (s) => s.length >= 6 && new TextEncoder().encode(s).length <= 72 },
  { id: "min",  texto: "Uma letra minúscula", falta: "uma letra minúscula",
    ok: (s) => /[a-z]/.test(s) },
  { id: "mai",  texto: "Uma letra maiúscula", falta: "uma letra maiúscula",
    ok: (s) => /[A-Z]/.test(s) },
  { id: "num",  texto: "Um número", falta: "um número",
    ok: (s) => /\d/.test(s) },
  { id: "simb", texto: "Um símbolo: @ $ ! % * ? & _ .", falta: "um símbolo (@ $ ! % * ? & _ .)",
    ok: (s) => /[@$!%*?&_.]/.test(s) },
  { id: "perm", texto: "Sem acentos, espaços ou outros símbolos", falta: "só letras sem acento, números e os símbolos @ $ ! % * ? & _ .",
    ok: (s) => /^[A-Za-z\d@$!%*?&_.]*$/.test(s) },
];

function senhaFaltas(senha) {
  return SENHA_REGRAS.filter((r) => !r.ok(senha)).map((r) => r.falta);
}

// Checklist ao vivo: cada item marca ✓ ou ○ (não depende só de cor)
const senhaInput = document.getElementById("cadastroSenha");
const senhaLista = document.getElementById("senhaRegras");

function atualizarRegrasSenha() {
  const tocou = senhaInput.value.length > 0;
  senhaLista.innerHTML = "";
  SENHA_REGRAS.forEach((r) => {
    const ok = tocou && r.ok(senhaInput.value);
    const li = document.createElement("li");
    li.className = ok ? "ok" : tocou ? "pendente" : "";
    li.textContent = `${ok ? "✓" : "○"} ${r.texto}`;
    senhaLista.appendChild(li);
  });
}

senhaInput.addEventListener("input", atualizarRegrasSenha);
atualizarRegrasSenha();

/* Troca mensagens cruas da API (regex do Pydantic etc.) por texto útil */
function mensagemApi(erro, contexto) {
  const texto = erro && erro.message ? erro.message : "";
  const cru = /pattern|should match|String should|HTTP 422/i.test(texto);

  if (contexto === "login") {
    // Não revela as regras nem se o e-mail existe
    return cru ? "E-mail ou senha incorretos." : texto || "E-mail ou senha incorretos.";
  }
  if (cru) {
    return "Dados inválidos. Confira a senha: de 6 a 72 caracteres, com minúscula, maiúscula, número e um símbolo (@ $ ! % * ? & _ .).";
  }
  return texto || "Erro ao criar o perfil.";
}

/* =========================================================
   CARREGAR CURSOS E TURMAS
   Busca as opções disponíveis na API e preenche os campos
   do formulário de cadastro.
========================================================= */

async function carregarOpcoesCadastro() {
  try {
    const { courses, classes } = await loadRegistrationOptions();

    const cursoSelect = document.getElementById("cadastroCurso");
    const turmaInput = document.getElementById("cadastroTurma");

    // Preenche o campo de cursos com os dados da API
    cursoSelect.innerHTML = `
            <option value="">
                Selecione seu curso
            </option>
        `;

    courses.forEach((curso) => {
      const option = document.createElement("option");

      // O ID é enviado para a API e o nome é exibido na tela
      option.value = curso.id;
      option.textContent = curso.course;

      cursoSelect.appendChild(option);
    });

    // Cria um campo de seleção para as turmas
    const turmaSelect = document.createElement("select");

    turmaSelect.id = "cadastroTurma";
    turmaSelect.required = true;

    turmaSelect.innerHTML = `
            <option value="">
                Selecione sua turma
            </option>
        `;

    classes.forEach((turma) => {
      const option = document.createElement("option");

      option.value = turma.id;
      option.textContent = turma.class_code;

      turmaSelect.appendChild(option);
    });

    // Substitui o campo de texto original pelo select
    turmaInput.replaceWith(turmaSelect);
  } catch (erro) {
    console.error("Erro ao carregar cursos e turmas:", erro);

    mostrarMensagem("Não foi possível carregar cursos e turmas.");
  }
}

/* =========================================================
   NAVEGAÇÃO ENTRE LOGIN E CADASTRO
========================================================= */

function mostrarCadastro() {
  loginForm.classList.remove("active");
  cadastroForm.classList.add("active");
}

function mostrarLogin() {
  cadastroForm.classList.remove("active");
  loginForm.classList.add("active");
}

/* =========================================================
   CADASTRO
   Valida os dados básicos e envia as informações para a API.
========================================================= */

criarContaForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  const nome = document.getElementById("cadastroNome").value.trim();
  const ra = document.getElementById("cadastroRA").value.trim();
  const email = document.getElementById("cadastroEmail").value.trim();

  const senha = document.getElementById("cadastroSenha").value;
  const confirmarSenha = document.getElementById("confirmarSenha").value;

  const curso = document.getElementById("cadastroCurso").value;
  const turma = document.getElementById("cadastroTurma").value;

  // Valida o nome
  if (nome.length < 3 || nome.length > 60) {
    mostrarMensagem("O nome deve ter entre 3 e 60 caracteres.");
    return;
  }

  // Valida o RA
  if (!/^\d{6}$/.test(ra)) {
    mostrarMensagem("O RA deve conter exatamente 6 números.");
    return;
  }

  // Valida a senha com as mesmas regras do backend
  const faltas = senhaFaltas(senha);
  if (faltas.length) {
    mostrarMensagem(`Senha inválida. Ela precisa ter: ${faltas.join("; ")}.`);
    document.getElementById("cadastroSenha").focus();
    return;
  }

  // Verifica se as senhas são iguais
  if (senha !== confirmarSenha) {
    mostrarMensagem("As senhas não são iguais!");
    return;
  }

  // Verifica curso e turma
  if (!curso) {
    mostrarMensagem("Selecione seu curso.");
    return;
  }

  if (!turma) {
    mostrarMensagem("Selecione sua turma.");
    return;
  }

  // Formato esperado pelo endpoint de cadastro
  const userData = {
    name: nome,
    ra: ra,
    email: email,
    password: senha,
    course: Number(curso),
    user_class: Number(turma),
  };

  try {
    mostrarMensagem("Criando seu perfil...");

    // Envia os dados através da camada de autenticação
    const resposta = await register(userData);

    console.log("Usuário criado:", resposta);

    mostrarMensagem("Perfil criado com sucesso!");

    criarContaForm.reset();

    // Após o cadastro, retorna para a tela de login
    setTimeout(() => {
      mostrarLogin();
    }, 1000);
  } catch (erro) {
    console.error("Erro ao criar perfil:", erro);

    mostrarMensagem(mensagemApi(erro, "cadastro"));
  }
});

/* =========================================================
   LOGIN
   Envia o e-mail e a senha e redireciona o usuário após
   a autenticação.
========================================================= */

entrarForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  const email = document.getElementById("loginEmail").value.trim();
  const senha = document.getElementById("loginSenha").value;

  try {
    mostrarMensagem("Entrando...");

    // Realiza o login através da camada de autenticação
    const resposta = await login(email, senha);

    console.log("Login realizado:", resposta);

    // Mantém o e-mail disponível para uso no frontend
    localStorage.setItem("usuarioEmail", email);

    mostrarMensagem("Login realizado com sucesso!");

    // Redireciona para a página principal
    setTimeout(() => {
      window.location.href = "index.html";
    }, 800);
  } catch (erro) {
    console.error("Erro ao fazer login:", erro);

    mostrarMensagem(mensagemApi(erro, "login"));
  }
});

/* =========================================================
   MENSAGENS
   Exibe mensagens temporárias para o usuário.
========================================================= */

let messageTimeout;

function mostrarMensagem(texto) {
  clearTimeout(messageTimeout);

  message.textContent = texto;
  message.classList.add("show");

  // Mensagem longa precisa de mais tempo de leitura
  messageTimeout = setTimeout(() => {
    message.classList.remove("show");
  }, Math.max(3000, texto.length * 70));
}

/* =========================================================
   INICIALIZAÇÃO
   Carrega cursos e turmas assim que a página é aberta.
========================================================= */

carregarOpcoesCadastro();
