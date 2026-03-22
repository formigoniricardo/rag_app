# rag_core.py
from dotenv import load_dotenv
import os
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from make_chunks import carregar_e_dividir_chunks


load_dotenv()
raw_api = os.getenv("CHAVE_API_GOOGLE")
api_key = SecretStr(raw_api) if raw_api else None


def criar_rag_chain(caminho_dados=None):
    """
    Cria e retorna uma cadeia RAG pronta para uso.
    Args:
        caminho_dados (str, opcional): caminho para o arquivo de dados.
                                       Se None, usa o padrão.
    Returns:
        Runnable: cadeia RAG pronta para .invoke(pergunta)
    """

    if caminho_dados is None:
        caminho_dados = r"usando API do google/data/wiki_nexus_monitor.txt"
    chunks = carregar_e_dividir_chunks(caminho_dados)

    embedding_model = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=api_key
    )
    vectorstore = FAISS.from_documents(
        documents=chunks, embedding=embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # Essa parte e a llm
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("CHAVE_API_GOOGLE"),
        temperature=0.4
    )
    template = """
Você é um assistente homem, gentil e útil da empresa TechVision Solutions, chamado Ulos.
Responda com base nas informações a seguir.
Se não houver dados suficientes, explique isso de forma educada e tente dar um contexto útil.

Contexto:
{context}

Pergunta: {question}

Resposta:
"""
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt  # <- Piper
        | llm
        | StrOutputParser()
    )
    return rag_chain
