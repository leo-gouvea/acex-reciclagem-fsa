CREATE DATABASE IF NOT EXISTS ecohora
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ecohora;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ra VARCHAR(20) NOT NULL UNIQUE,
    curso VARCHAR(100) NOT NULL,
    turma VARCHAR(50),
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('aluno', 'operador', 'admin') NOT NULL DEFAULT 'aluno',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reciclagens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    material VARCHAR(50) NOT NULL,
    peso DECIMAL(10,2) NOT NULL,
    data_entrega TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pendente', 'validada', 'cancelada') NOT NULL DEFAULT 'pendente',

    CONSTRAINT fk_reciclagem_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);