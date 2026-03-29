# app_postgres.py
import streamlit as st
from rag_core import criar_rag_chain


st.title("Assistente da TechVision (PostgreSQL)")

pergunta = st.text_input("Faça uma pergunta:")


if "rag_chain" not in st.session_state:
    with st.spinner("Inicializando o assistente..."):
        st.session_state.rag_chain = criar_rag_chain()
    st.success("Estou pronto!")

if pergunta:
    with st.spinner("Pensando..."):
        resposta = st.session_state.rag_chain.invoke(pergunta)

    st.write("🤖 **Resposta:**")
    st.write(resposta)
