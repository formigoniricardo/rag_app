-- Executado automaticamente na primeira inicialização do container PostgreSQL.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documentos (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255),
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER,
    section VARCHAR(255),
    embedding VECTOR(3072),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
