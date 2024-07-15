CREATE DATABASE billetera_yape;

\c billetera_yape;

CREATE TABLE cuentausuario(
    numero VARCHAR(9) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    saldo INT NOT NULL
);

CREATE TABLE contacto(
    id SERIAL PRIMARY KEY,
    numero_usuario VARCHAR(9) REFERENCES cuentausuario(numero),
    numero_contacto VARCHAR(9) REFERENCES cuentausuario(numero),
    UNIQUE(numero_usuario, numero_contacto)
);

CREATE TABLE operacion(
    id SERIAL PRIMARY KEY,
    cuenta_origen VARCHAR(9) REFERENCES cuentausuario(numero),
    cuenta_destino VARCHAR(9) REFERENCES cuentausuario(numero),
    valor INT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO cuentausuario (numero, nombre, saldo) VALUES
('21345', 'Arnaldo', 200),
('123', 'Luisa', 400),
('456', 'Andrea', 300);

INSERT INTO contacto (numero_usuario, numero_contacto) VALUES
('21345', '123'),
('21345', '456'),
('123', '456'),
('456', '21345');
