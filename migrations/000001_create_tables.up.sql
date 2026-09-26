CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    rubrics JSONB NOT NULL,
    created_date TIMESTAMP NOT NULL
);