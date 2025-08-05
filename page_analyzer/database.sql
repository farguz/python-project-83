CREATE TABLE IF NOT EXISTS urls (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP NOT NULL
    );

CREATE TABLE IF NOT EXISTS url_checks  (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        url_id BIGINT NOT NULL,
        status_code INT,
        h1 VARCHAR(255),
        title VARCHAR(255),
        description VARCHAR(255),
        created_at TIMESTAMP NOT NULL
    );