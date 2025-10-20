# dia4_rag_completo.py
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dia2_carregar_dados import carregar_e_dividir_chunks

load_dotenv()

# 1. Carregar chunks
chunks = carregar_e_dividir_chunks(r"usando API do google\data\dados_empresa.txt")

# 2. Criar vector store e retriever
def rag_chain(chunks):
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("CHAVE_API_GOOGLE")
    )
    vectorstore = FAISS.from_documents(documents=chunks, embedding=embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})  # só 2 chunks

    # 3. Criar LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("CHAVE_API_GOOGLE"),
        temperature=0.2
    )

    # 4. Montar prompt e cadeia RAG
    template = """
    Você é um assistente gentil e útil da TechVision Solutions.
    Responda à pergunta do usuário com base **apenas** nas seguintes informações.
    Se a informação não estiver disponível, diga gentilmente que não sabe sobre a informação.

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

# 5. Testar
print("🤖 Assistente da TechVision pronto! Digite 'sair' para encerrar.\n")

pergunta = input("💬 Faça uma pergunta: ").strip()
resposta = rag_chain.invoke(pergunta)
print(f"🤖 {resposta}")
