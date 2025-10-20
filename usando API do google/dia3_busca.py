from dotenv import load_dotenv
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from dia2_carregar_dados import carregar_e_dividir_chunks  # ← Importa a função!

load_dotenv()

# 1. Obter chunks do Dia 2
chunks = carregar_e_dividir_chunks(r"usando API do google\data\dados_empresa.txt")
# print(chunks[0].page_content)

# 2. Criar embeddings e vector store
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("CHAVE_API_GOOGLE")
)

vectorstore = FAISS.from_documents(documents=chunks, embedding=embedding_model)
retriever = vectorstore.as_retriever()

# 3. Testar
pergunta = "Qual é a razão social"
resultados = retriever.invoke(pergunta)

print(f"🔍 Encontrados {len(resultados)} chunks relevantes:\n")


for i, doc in enumerate(resultados):
    print(f"📄 Chunk {i+1}:")
    print(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
    print("-" * 50)