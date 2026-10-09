const API_BASE_URL = "https://apei-ecohora.discloud.app";
// const API_BASE_URL = "http://127.0.0.1:8000"; // Endereço da API para testes. Terminal -> http://127.0.0.1:8000

async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            ...options.headers
        }
    });

    let data;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        let message = `HTTP ${response.status}`;

        if (data?.detail) {

            // Erro simples: "E-mail ou senha incorretos."
            if (typeof data.detail === "string") {
                message = data.detail;
            }

            // Erros de validação do FastAPI
            else if (Array.isArray(data.detail)) {
                message = data.detail
                    .map(error => {

                        if (typeof error === "string") {
                            return error;
                        }

                        return (
                            error.msg ||
                            error.message ||
                            JSON.stringify(error)
                        );
                    })
                    .join("\n");
            }

            // Caso detail seja um objeto
            else if (typeof data.detail === "object") {
                message =
                    data.detail.msg ||
                    data.detail.message ||
                    JSON.stringify(data.detail);
            }
        }

        else if (data?.message) {
            message =
                typeof data.message === "string"
                    ? data.message
                    : JSON.stringify(data.message);
        }

        else if (data?.error) {
            message =
                typeof data.error === "string"
                    ? data.error
                    : JSON.stringify(data.error);
        }

        throw new Error(message);
    }

    return data;
}


/* =========================================================
   USUÁRIO
========================================================= */

async function registerUser(userData) {
    return apiRequest("/user/register", {
        method: "POST",
        body: JSON.stringify(userData)
    });
}


async function loginUser(email, password) {
    return apiRequest("/user/login", {
        method: "POST",
        body: JSON.stringify({
            email,
            password
        })
    });
}


async function getUser(userRa) {
    return apiRequest(`/user/get/${userRa}`, {
        method: "GET"
    });
}

async function updateUser(userData) {
    return apiRequest("/user/update", {
        method: "PATCH",
        body: JSON.stringify(userData)
    });
}

async function checkSession() {
    return apiRequest("/user/session", {
        method: "GET"
    });
}

async function logoutUser() {
    return apiRequest("/user/logout", {
        method: "POST"
    });
}


/* =========================================================
   FSA
========================================================= */

async function getCourses() {
    return apiRequest("/fsa/get/courses", {
        method: "GET"
    });
}


async function getClasses() {
    return apiRequest("/fsa/get/classes", {
        method: "GET"
    });
}

/* =========================================================
   RECICLAGEM
========================================================= */

async function getMaterials() {
    return apiRequest("/recycling/materials-info", {
        method: "GET"
    });
}


async function registerRecycling(recyclingData) {
    return apiRequest("/recycling/recycle", {
        method: "POST",
        body: JSON.stringify(recyclingData)
    });
}


async function deleteRecycling(recyclingId) {
    return apiRequest(`/recycling/recycle/${recyclingId}`, {
        method: "DELETE"
    });
}
