# rag_core.py
"""
Núcleo do RAG — Oráculo Corporativo.

Busca vetorial direta na tabela `documentos` (pgvector) + Google Gemini.
Toda configuração é via variáveis de ambiente (.env local ou App Settings).
"""
import json
import os
import tempfile
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
LLM_MODEL       = os.getenv("LLM_MODEL", "gemini-2.5-flash")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.4"))
RAG_TOP_K       = int(os.getenv("RAG_TOP_K", "5"))

TEMPLATE = """
Você é um assistente homem, gentil e útil da empresa TechVision Solutions, chamado Ulos.
Responda com base nas informações a seguir.
Se não houver dados suficientes, explique isso de forma educada e tente dar um contexto útil.

Contexto:
{context}

Pergunta: {question}

Resposta:
"""


def get_connection():
    """Conexão Postgres via env (DATABASE_URL ou variáveis separadas)."""
    url = os.getenv("DATABASE_URL")
    if url:
        return psycopg2.connect(url)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "rag_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "senha123"),
        sslmode=os.getenv("DB_SSLMODE", "prefer"),
    )


def _vec(embedding):
    """Lista de floats → literal pgvector '[x,y,z]'."""
    return "[" + ",".join(repr(float(x)) for x in embedding) + "]"


def garantir_schema():
    """Cria extensão + tabela se não existirem (idempotente)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("""
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
            """)
        conn.commit()
    finally:
        conn.close()


# ─────────────────────── Ingestão (upload) ───────────────────────

def indexar_arquivo(conteudo_bytes: bytes, nome_arquivo: str,
                    on_progress=None) -> int:
    """Recebe bytes de um arquivo .txt, faz chunking+embedding e grava no banco.
    Retorna a quantidade de chunks inseridos. `on_progress(msg)` é callback opcional."""
    from insert_data_in_database.make_chunks import carregar_e_dividir_chunks

    raw_api = os.getenv("CHAVE_API_GOOGLE")
    api_key = SecretStr(raw_api) if raw_api else None

    # salvar temporariamente para o TextLoader do LangChain
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(conteudo_bytes)
        tmp_path = tmp.name

    try:
        if on_progress:
            on_progress("Fragmentando texto...")
        chunks = carregar_e_dividir_chunks(tmp_path)

        if on_progress:
            on_progress(f"Gerando embeddings ({len(chunks)} chunks)...")
        emb_model = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, api_key=api_key)
        textos = [c.page_content for c in chunks]
        embeddings = emb_model.embed_documents(textos)

        if on_progress:
            on_progress("Gravando no banco...")
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                from psycopg2.extras import execute_values
                dados = [
                    (nome_arquivo, c.page_content, i, "UPLOAD",
                     _vec(e), json.dumps({"source": nome_arquivo}))
                    for i, (c, e) in enumerate(zip(chunks, embeddings))
                ]
                execute_values(
                    cur,
                    """INSERT INTO documentos
                       (document_id, chunk_text, chunk_index, section, embedding, metadata)
                       VALUES %s""",
                    dados,
                    template="(%s, %s, %s, %s, %s::vector, %s)",
                )
            conn.commit()
        finally:
            conn.close()
    finally:
        os.unlink(tmp_path)

    return len(chunks)


def limpar_base():
    """Remove todos os documentos da tabela (RF09)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM documentos;")
        conn.commit()
    finally:
        conn.close()


def contar_documentos() -> int:
    """Total de chunks na base."""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM documentos;")
                return cur.fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ─────────────────────── Cadeia RAG ───────────────────────

class RagChain:
    """Cadeia RAG: pergunta → embedding → busca vetorial → prompt → LLM → resposta."""

    def __init__(self, temperatura: float = LLM_TEMPERATURE):
        raw_api = os.getenv("CHAVE_API_GOOGLE")
        api_key = SecretStr(raw_api) if raw_api else None

        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL, api_key=api_key,
        )
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=raw_api,
            temperature=temperatura,
        )
        self.prompt  = ChatPromptTemplate.from_template(TEMPLATE)
        self.parser  = StrOutputParser()

    def buscar_documentos(self, pergunta: str, k: int = RAG_TOP_K):
        vetor = _vec(self.embedding_model.embed_query(pergunta))
        sql = """
            SELECT chunk_text, document_id, section,
                   1 - (embedding <=> %s::vector) AS similaridade
            FROM documentos
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (vetor, vetor, k))
                return [
                    {"texto": r[0], "fonte": r[1], "secao": r[2],
                     "similaridade": float(r[3])}
                    for r in cur.fetchall()
                ]
        finally:
            conn.close()

    def responder(self, pergunta: str) -> dict:
        docs = self.buscar_documentos(pergunta)
        ctx = ("\n\n".join(
            f"[Fonte: {d['fonte']} | Seção: {d['secao']}]\n{d['texto']}"
            for d in docs
        ) if docs else "Nenhum documento na base de conhecimento.")

        msgs = self.prompt.invoke({"context": ctx, "question": pergunta})
        resp = self.parser.invoke(self.llm.invoke(msgs))
        return {"resposta": resp, "fontes": docs}

    def invoke(self, pergunta: str) -> str:
        return self.responder(pergunta)["resposta"]


def criar_rag_chain(temperatura: float = LLM_TEMPERATURE) -> RagChain:
    return RagChain(temperatura=temperatura)
