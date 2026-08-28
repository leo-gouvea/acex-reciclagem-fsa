const PASSWORD_PATTERN =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_.])[A-Za-z\d@$!%*?&_.]+$/;


function validateRegistrationData(data) {
    const errors = {};

    if (!data.name || data.name.length < 3 || data.name.length > 60) {
        errors.name = "O nome deve possuir entre 3 e 60 caracteres.";
    }

    if (!data.ra || !/^\d{6}$/.test(data.ra)) {
        errors.ra = "O RA deve possuir exatamente 6 números.";
    }

    if (!data.email) {
        errors.email = "O e-mail é obrigatório.";
    } else {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailPattern.test(data.email)) {
            errors.email = "Informe um e-mail válido.";
        }
    }

    if (!data.password || data.password.length < 6) {
        errors.password = "A senha deve possuir pelo menos 6 caracteres.";
    } else if (!PASSWORD_PATTERN.test(data.password)) {
        errors.password =
            "A senha deve conter letra maiúscula, minúscula, número e símbolo.";
    }

    if (!data.course) {
        errors.course = "Selecione um curso.";
    }

    if (!data.user_class) {
        errors.user_class = "Selecione uma turma.";
    }

    return {
        valid: Object.keys(errors).length === 0,
        errors
    };
}
