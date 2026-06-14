# interface_main.py — Oráculo Corporativo (Streamlit)
"""
Interface de chat com:
  RF01  Upload de arquivos (.txt)
  RF08  Histórico de mensagens na sessão
  RF09  Limpeza / reinício da base de dados
  RF10  Indicadores de status (spinners)
  RF11  Ajuste de temperatura da IA
  RF12  Citação de fontes recuperadas
"""
import streamlit as st
from rag_core import criar_rag_chain, indexar_arquivo, limpar_base, contar_documentos

# ────────────── Página ──────────────
st.set_page_config(page_title="Oráculo Corporativo", page_icon="🔮", layout="centered")

# ────────────── Sidebar ──────────────
with st.sidebar:
    st.header("⚙️ Configurações")

    temperatura = st.slider("Temperatura da IA (RF11)", 0.0, 1.0, 0.4, 0.05)

    st.divider()

    # RF01 — Upload de documentos
    st.subheader("📄 Upload de documentos")
    arquivo = st.file_uploader("Envie um arquivo .txt", type=["txt"])
    if arquivo and st.button("Indexar arquivo"):
        placeholder = st.empty()
        try:
            n = indexar_arquivo(
                arquivo.getvalue(),
                arquivo.name,
                on_progress=lambda msg: placeholder.info(msg),
            )
            placeholder.success(f"✅ {n} chunks indexados de **{arquivo.name}**!")
        except Exception as e:
            placeholder.error(f"Erro: {e}")

    st.divider()

    # Contador + RF09 — Reset
    total = contar_documentos()
    st.metric("Chunks na base", total)
    if total > 0 and st.button("🗑️ Limpar toda a base"):
        limpar_base()
        st.success("Base limpa!")
        st.rerun()

# ────────────── Chat principal ──────────────
st.title("🔮 Oráculo Corporativo")
st.caption("RAG AI — Pergunte sobre os documentos indexados")

# RF08 — Histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Recria a chain se a temperatura mudou
if ("rag_chain" not in st.session_state
        or st.session_state.get("_temp") != temperatura):
    with st.spinner("Inicializando o assistente..."):
        st.session_state.rag_chain = criar_rag_chain(temperatura=temperatura)
        st.session_state._temp = temperatura

# Exibir mensagens anteriores
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("fontes"):
            with st.expander("📚 Fontes"):
                for f in msg["fontes"]:
                    st.markdown(
                        f"- **{f['fonte']}** (seção: {f['secao']}, "
                        f"sim: {f['similaridade']:.3f})"
                    )

# Input do usuário
if pergunta := st.chat_input("Faça uma pergunta ao Oráculo..."):
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando a base de conhecimento..."):  # RF10
            resultado = st.session_state.rag_chain.responder(pergunta)

        st.markdown(resultado["resposta"])

        # RF12 — Fontes
        if resultado["fontes"]:
            with st.expander("📚 Fontes consultadas"):
                for f in resultado["fontes"]:
                    st.markdown(
                        f"- **{f['fonte']}** (seção: {f['secao']}, "
                        f"sim: {f['similaridade']:.3f})"
                    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": resultado["resposta"],
        "fontes": resultado["fontes"],
    })
