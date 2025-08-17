import streamlit as st
import random

st.title("📣 Feed de Updates (demo)")

if "updates" not in st.session_state:
    st.session_state.updates = [
        {"autor":"Startup Alpha","texto":"Batemos 1.000 clientes e abrimos rodada seed.","quando":"há 2 dias"},
        {"autor":"HealthTrack","texto":"Piloto com 3 hospitais. Procurando smart money em saúde.","quando":"há 5 dias"},
    ]

with st.form("novo_update"):
    st.write("Publique um update (demo)")
    autor = st.text_input("Autor", value=st.session_state.get("my_name","Você"))
    texto = st.text_area("Texto", "")
    enviado = st.form_submit_button("Publicar")
    if enviado and texto.strip():
        st.session_state.updates.insert(0, {"autor": autor, "texto": texto.strip(), "quando": "agora"})
        st.success("Publicado!")

st.markdown("---")
for i,u in enumerate(st.session_state.updates):
    with st.container(border=True):
        st.markdown(f"**{u['autor']}** · {u['quando']}")
        st.write(u["texto"])
        if st.button("Seguir", key=f"seg_{i}"):
            st.success("Agora você segue este perfil (demo).")
