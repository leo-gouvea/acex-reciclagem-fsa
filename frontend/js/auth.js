async function register(userData) {
    return registerUser(userData);
}

async function login(email, password) {
    return loginUser(email, password);
}

async function getAuthenticatedUser(userRa) {
    return getUser(userRa);
}