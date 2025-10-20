from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()
gemini_api_google = os.getenv('CHAVE_API_GOOGLE')

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=gemini_api_google,
    temperature=0.2
)

pergunta = "O que é inteligência artificial? Responda em português, bem explicativo!"
mensagens = [HumanMessage(content=pergunta)]

for chunk in llm.stream(mensagens):
    print(chunk.content, end='', flush=True)

