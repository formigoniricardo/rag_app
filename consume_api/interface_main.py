# Esse aqui e a barte web
import streamlit as st
from rag_core import criar_rag_chain

st.title("Assistente da TechVision")
pergunta = st.text_input("Faça uma pergunta:")

# Cria a cadeia uma vez (Streamlit reexecuta o script a cada interação)
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = criar_rag_chain()

if pergunta:
    resposta = st.session_state.rag_chain.invoke(pergunta)
    st.write("😁", resposta)
