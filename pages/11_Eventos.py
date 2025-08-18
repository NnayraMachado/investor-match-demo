import streamlit as st
import datetime as dt

st.set_page_config(page_title="Eventos", page_icon="🎤", layout="centered")
st.title("🎤 Demo Days & Eventos")

events = [
    {"data": dt.date.today()+dt.timedelta(days=5), "titulo":"Demo Day — SaaS/AI", "vagas": 50},
    {"data": dt.date.today()+dt.timedelta(days=12), "titulo":"Pitch Night — Health/Climate", "vagas": 40},
    {"data": dt.date.today()+dt.timedelta(days=21), "titulo":"Investor Roundtable — Seed", "vagas": 25},
]

for i,e in enumerate(events):
    with st.container(border=True):
        st.subheader(e["titulo"])
        st.caption(e["data"].strftime("%d/%m/%Y"))
        st.caption(f"Vagas: {e['vagas']}")
        if st.session_state.get("user_plan")!="Pro":
            st.button("Participar (Pro)", key=f"join_{i}", disabled=True)
            st.warning("🔒 Eventos exclusivos do Pro. Faça upgrade para reservar vaga.")
        else:
            if st.button("Participar", key=f"join_{i}"):
                st.success("Inscrição realizada! Você receberá um e-mail com detalhes (demo).")
