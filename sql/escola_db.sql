-- Cria um banco de dados
CREATE DATABASE IF NOT EXISTS escola_db;
USE escola_db;
-- 1. Tabela Professor (Não depende de ninguém)
CREATE TABLE IF NOT EXISTS Professor (
    id_professor INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    rua VARCHAR(255),
    numero VARCHAR(20),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado CHAR(2),
    telefone VARCHAR(30)
);
-- 2. Tabela Aluno (Não depende de ninguém)
CREATE TABLE IF NOT EXISTS Aluno (
    id_aluno INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    rua VARCHAR(255),
    numero VARCHAR(20),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado CHAR(2),
    telefone VARCHAR(30)
);
-- 3. Tabela Disciplina (Depende de Professor)
CREATE TABLE IF NOT EXISTS Disciplina (
    id_disciplina INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    horario VARCHAR(100),
    id_professor_ministrante INT,
    FOREIGN KEY (id_professor_ministrante) REFERENCES Professor(id_professor) ON DELETE
    SET NULL ON UPDATE CASCADE
);
-- 4. Tabela Matricula (Tabela Associativa N:M)
CREATE TABLE IF NOT EXISTS Matricula (
    id_aluno INT,
    id_disciplina INT,
    nota1 DECIMAL(4, 2),
    nota2 DECIMAL(4, 2),
    nota3 DECIMAL(4, 2),
    nota4 DECIMAL(4, 2),
    PRIMARY KEY (id_aluno, id_disciplina),
    FOREIGN KEY (id_aluno) REFERENCES Aluno(id_aluno) ON DELETE CASCADE,
    FOREIGN KEY (id_disciplina) REFERENCES Disciplina(id_disciplina) ON DELETE CASCADE
);
-- 5. Tabela de Usuários Admin
CREATE TABLE IF NOT EXISTS Users (
    user VARCHAR(50) PRIMARY KEY,
    senha_hash VARCHAR(255) NOT NULL
);
-- Limpar tabelas antes de inserir para evitar duplicatas em testes
TRUNCATE TABLE Matricula;
TRUNCATE TABLE Disciplina;
TRUNCATE TABLE Aluno;
TRUNCATE TABLE Professor;
TRUNCATE TABLE Users;
-- Inserindo Professores
INSERT INTO Professor (
        nome,
        rua,
        numero,
        bairro,
        cidade,
        estado,
        telefone
    )
VALUES (
        'Dr. Carlos Xavier',
        'Rua das Flores',
        '123',
        'Centro',
        'São Paulo',
        'SP',
        '1199991111'
    ),
    (
        'Dra. Ana Beatriz',
        'Av. Paulista',
        '456',
        'Bela Vista',
        'São Paulo',
        'SP',
        '1199992222'
    ),
    (
        'Msc. Ricardo Lima',
        'Rua da Consolação',
        '789',
        'Jardins',
        'São Paulo',
        'SP',
        '1199993333'
    );
-- Inserindo Alunos
INSERT INTO Aluno (
        nome,
        rua,
        numero,
        bairro,
        cidade,
        estado,
        telefone
    )
VALUES (
        'Bruno Silva',
        'Rua A',
        '10',
        'Lapa',
        'Rio de Janeiro',
        'RJ',
        '2188881111'
    ),
    (
        'Mariana Costa',
        'Rua B',
        '20',
        'Tijuca',
        'Rio de Janeiro',
        'RJ',
        '2188882222'
    ),
    (
        'Felipe Souza',
        'Rua C',
        '30',
        'Copacabana',
        'Rio de Janeiro',
        'RJ',
        '2188883333'
    ),
    (
        'Juliana Oliveira',
        'Rua D',
        '40',
        'Botafogo',
        'Rio de Janeiro',
        'RJ',
        '2188884444'
    ),
    (
        'Lucas Martins',
        'Rua E',
        '50',
        'Flamengo',
        'Rio de Janeiro',
        'RJ',
        '2188885555'
    );
-- Inserindo Disciplinas
INSERT INTO Disciplina (nome, horario, id_professor_ministrante)
VALUES ('Matemática Discreta', 'Seg 08h-10h', 1),
    ('Banco de Dados I', 'Ter 10h-12h', 2),
    (
        'Programação Orientada a Objetos',
        'Qua 14h-16h',
        1
    ),
    ('Engenharia de Software', 'Qui 08h-10h', 3);
-- Inserindo Matrículas e Notas
INSERT INTO Matricula (
        id_aluno,
        id_disciplina,
        nota1,
        nota2,
        nota3,
        nota4
    )
VALUES (1, 1, 8.00, 7.50, 9.00, 8.50),
    (1, 2, 9.00, 9.50, 10.0, 9.00),
    (2, 2, 7.00, 8.00, 7.50, 7.00),
    (2, 4, 10.0, 9.50, 9.00, 10.0),
    (3, 1, 5.00, 6.50, 7.00, 6.00),
    (3, 3, 8.00, 8.50, 9.00, 8.00),
    (4, 1, 9.50, 9.00, 10.0, 9.00),
    (4, 2, 9.00, 8.50, 8.00, 9.00),
    (4, 3, 7.50, 8.00, 8.50, 7.00),
    (4, 4, 6.00, 7.00, 6.50, NULL),
    (5, 3, NULL, NULL, NULL, NULL);
-- Inserindo Usuários Admin (com senhas em MD5 para teste)
INSERT INTO Users (user, senha_hash)
VALUES ('admin', '21232f297a57a5a743894a0e4a801fc3'),
    -- senha: admin
    ('igor', 'dd97813dd40be87559aaefed642c3fbb'),
    -- senha: igor
    ('judiy', 'd3123d3f70618c63b46d7a66444499de');
-- senha: judiy