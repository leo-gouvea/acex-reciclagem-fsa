const API_BASE_URL = "https://apei-ecohora.discloud.app";

async function apiRequest(endpoint, options = {}) {
    const apiKey = window.TEMP_API_KEY;

    if (!apiKey) {
        throw new Error("API Key não fornecida. Por favor, insira a chave no campo de entrada.");
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": apiKey,
            ...options.headers
        }
    });

    const data = await response.json();

    if (!response.ok) {
        const message =
            data.detail ||
            data.message ||
            data.error ||
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
        body: JSON.stringify({ email, password })
    });
}

async function getUser(userId) {
    // This will now automatically use the key from window.TEMP_API_KEY
    return apiRequest(`/user/get/${userId}`, {
        method: "GET"
    });
}