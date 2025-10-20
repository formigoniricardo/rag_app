import streamlit as st
from dia4_rag_completo import rag_chain  # se você modularizar

st.title("Assistente da TechVision")
pergunta = st.text_input("Faça uma pergunta:")
if pergunta:
    resposta = rag_chain.invoke(pergunta)
    st.write("🤖", resposta)