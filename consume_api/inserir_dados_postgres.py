# inserir_dados_postgres.py
import psycopg2
from psycopg2.extras import execute_values
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from make_chunks import carregar_e_dividir_chunks
from dotenv import load_dotenv
import os
from pydantic import SecretStr
import json

# Carregar variáveis de ambiente
load_dotenv()
raw_api = os.getenv("CHAVE_API_GOOGLE")
api_key = SecretStr(raw_api) if raw_api else None

# Conectar ao PostgreSQL
print("🔌 Conectando ao PostgreSQL...")
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="rag_db",
    user="postgres",
    password="senha123"
)
cur = conn.cursor()
print("✅ Conexão estabelecida!")

# Carregar chunks do arquivo
print("\n📄 Carregando chunks do arquivo...")
chunks = carregar_e_dividir_chunks("consume_api/data/wiki_nexus_monitor.txt")
print(f"✅ {len(chunks)} chunks carregados")

# Criar modelo de embeddings
print("\n🧠 Criando modelo de embeddings...")
embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=api_key
)
print("✅ Modelo de embeddings criado!")

# Gerar embeddings para cada chunk
print("\n🔄 Gerando embeddings para cada chunk...")
embeddings = []
for i, chunk in enumerate(chunks):
    print(f"  Chunk {i+1}/{len(chunks)}...", end="\r")
    embedding = embedding_model.embed_query(chunk.page_content)
    embeddings.append(embedding)
print(f"\n✅ {len(embeddings)} embeddings gerados!")

# Preparar dados para inserção
print("\n📦 Preparando dados para inserção...")
dados = []
for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    metadata_dict = {"source": "wiki"}  # ← Dicionário Python
    metadata_json = json.dumps(metadata_dict)  # ← Converter para string JSON
    dados.append((
        "wiki_nexus_monitor.txt",
        chunk.page_content,
        i,
        "SEÇÃO_DESCONHECIDA",
        embedding,
        metadata_json  # ← Agora é string JSON, não dict
    ))
print("✅ Dados preparados!")

# Inserir dados na tabela
print("\n💾 Inserindo dados no banco...")
execute_values(
    cur,
    """
    INSERT INTO documentos 
    (document_id, chunk_text, chunk_index, section, embedding, metadata)
    VALUES %s
    """,
    dados
)
conn.commit()
print(f"✅ {len(dados)} registros inseridos!")

# Fechar conexão
cur.close()
conn.close()
print("\n👋 Conexão fechada!")

print("\n🎉 Dados inseridos com sucesso!")