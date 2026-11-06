create database tlcoa;
USE tlcoa;

DROP TABLE IF EXISTS profesores;
CREATE TABLE profesores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    especialidad VARCHAR(50) NOT NULL
);

INSERT INTO profesores (nombre, especialidad) VALUES
('Marcela Danrez', 'Acuarela'),
('Martina Careliez', 'Acuarela'),
('Dlarid Samon', 'Ilustración Digital'),
('Dabrid Sammon', 'Pintura'),
('Danán Longo', 'Escultura');

DROP TABLE IF EXISTS cursos;
CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    horario VARCHAR(50) NOT NULL,
    dia VARCHAR(20) NOT NULL,
    id_profesor INT,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE SET NULL
);

INSERT INTO cursos (nombre, horario, dia, id_profesor) VALUES
('Acuarela', '18:00 - 20:00 hrs', 'Lunes', 1),
('Acuarela', '15:00 - 17:00 hrs', 'Martes', 2),
('Ilustración Digital', '16:00 - 18:00 hrs', 'Miércoles', 3),
('Pintura', '16:00 - 18:00 hrs', 'Jueves', 4),
('Escultura', '10:00 - 13:00 hrs', 'Viernes', 5);

DROP TABLE IF EXISTS alumnos;
CREATE TABLE alumnos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    grupo VARCHAR(10) NOT NULL,
    id_curso INT,
    FOREIGN KEY (id_curso) REFERENCES cursos(id) ON DELETE SET NULL
);

INSERT INTO alumnos (nombre, apellido, fecha_nacimiento, grupo, id_curso) VALUES
('María Fernanda', 'Gómez Pérez', '2002-05-14', '101', 1),
('David David', 'Atilano Rosas', '2001-09-20', '102', 3);