async function register(userData) {
    return registerUser(userData);
}

async function login(email, password) {
    return loginUser(email, password);
}

async function getAuthenticatedUser(userRa) {
    return getUser(userRa);
}

async function updateProfile(userData) {
    return updateUser(userData);
}

async function loadRegistrationOptions() {
    const [courses, classes] = await Promise.all([
        getCourses(),
        getClasses()
    ]);

    return {
        courses,
        classes
    };
}