// const API_BASE_URL = "https://apei-ecohora.discloud.app";
const API_BASE_URL = "http://127.0.0.1:8000"; // Endereço para testes

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
        const message =
            data?.detail ||
            data?.message ||
            data?.error ||
            `HTTP ${response.status}`;

        throw new Error(message);
    }

    return data;
}

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

async function getUser(userId) {
    return apiRequest(`/user/get/${userId}`, {
        method: "GET"
    });
}