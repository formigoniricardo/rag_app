# rag_core.py
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from dia2_carregar_dados import carregar_e_dividir_chunks

# Carrega a chave uma vez
load_dotenv()

def criar_rag_chain(caminho_dados=None):
    """
    Cria e retorna uma cadeia RAG pronta para uso.
    
    Args:
        caminho_dados (str, opcional): caminho para o arquivo de dados.
                                       Se None, usa o padrão.
    
    Returns:
        Runnable: cadeia RAG pronta para .invoke(pergunta)
    """
    # 1. Carregar chunks
    if caminho_dados is None:
        caminho_dados = r"usando API do google\data\dados_empresa.txt"
    chunks = carregar_e_dividir_chunks(caminho_dados)

    # 2. Criar embeddings e vector store
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("CHAVE_API_GOOGLE")
    )
    vectorstore = FAISS.from_documents(documents=chunks, embedding=embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    # 3. Criar LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",  # ✅ modelo ativo (não 2.5-flash, que pode estar em preview)
        google_api_key=os.getenv("CHAVE_API_GOOGLE"),
        temperature=0.2
    )

    # 4. Montar prompt e cadeia
    template = """
Você é um assistente gentil e útil da empresa TechVision Solutions, quando for se apresentar apenas diga seu nome, você se chama Lexia.
Responda à pergunta do usuário com base **apenas** nas seguintes informações.
Se a informação não estiver disponível, crie e diga gentilmente uma frase que faça entender que você não sabe sobre a informação.

Contexto:
{context}

Pergunta: {question}

Resposta:
"""
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain