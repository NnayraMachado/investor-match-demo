import streamlit as st
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILES_JSON = BASE_DIR / "assets" / "profiles.json"

@st.cache_data
def load_profiles():
    with open(PROFILES_JSON, "r", encoding="utf-8") as f:
        return json.load(f)
profiles = load_profiles()

_, mid, _ = st.columns([1,2,1])
with mid:
    st.markdown("## ✨ Deu Match!")
    st.balloons()

    me_name = st.session_state.get("my_name", "Você")
    my_photo = st.session_state.get("my_photo")
    idx = st.session_state.get("last_match_idx", None)
    if idx is None:
        st.info("Sem match recente. Volte ao **Explorar**.")
        st.page_link("pages/02_Swipe.py", label="Voltar ao Swipe")
        st.stop()

    other = profiles[idx % len(profiles)]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{me_name}**")
        if my_photo:
            st.image(my_photo, width=200, caption=me_name)
        else:
            st.image("assets/profiles/profile_1.png", width=200, caption=me_name)
    with col2:
        st.markdown(f"**{other['name']}**")
        st.image(other["image"], width=200, caption=other["name"])

    st.success("Agora vocês podem conversar e agendar uma call.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💬 Abrir Chat"):
            key_history = f"chat_history_{idx}"
            if key_history not in st.session_state:
                st.session_state[key_history] = []
            if not any(a=="Você" and "Prazer em conectar!" in t for a,t,_ in st.session_state[key_history]):
                st.session_state[key_history].append(("Você", "Prazer em conectar! Podemos alinhar um horário?", "delivered"))
            st.switch_page("pages/03_Mensagens.py")
    with c2:
        if st.button("➡️ Continuar swipando"):
            st.switch_page("pages/02_Swipe.py")
