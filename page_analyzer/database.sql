CREATE TABLE urls (
        id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        name varchar(255) NOT NULL,
        created_at TIMESTAMP
    );