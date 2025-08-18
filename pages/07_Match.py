import json
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def icon_of(p): return p.get("icon","💰" if p.get("type")=="investor" else "🚀")

st.set_page_config(page_title="Match", page_icon="✨", layout="centered")
st.markdown("""
<style>
.app { max-width: 420px; margin: 0 auto; text-align:center; }
.portrait { width: 160px; height: 160px; border-radius: 20px;
            background: #eef2f7; display:flex; align-items:center; justify-content:center; }
.portrait span { font-size: 84px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app">', unsafe_allow_html=True)
st.markdown("## ✨ Deu Match!")

pid = st.session_state.get("last_match_idx")
name = st.session_state.get("last_match_name", "Perfil")

profiles = load_profiles()
other = next((x for x in profiles if x.get("id")==pid), None)
icon_other = icon_of(other) if other else "💰"

colA, colB = st.columns(2)
with colA:
    st.markdown('<div class="portrait"><span>🙂</span></div>', unsafe_allow_html=True)
    st.caption("Você")
with colB:
    st.markdown(f'<div class="portrait"><span>{icon_other}</span></div>', unsafe_allow_html=True)
    st.caption(name)

st.success("Agora vocês podem conversar e abrir um Dealroom! 🎉")

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("💬 Mensagens", use_container_width=True):
        try: st.switch_page("pages/03_Mensagens.py")
        except Exception: st.info("Abra **Mensagens** no menu.")
with c2:
    if st.button("📂 Dealroom", use_container_width=True):
        st.switch_page("pages/09_Dealroom.py")
with c3:
    if st.button("🔙 Voltar ao Swipe", use_container_width=True):
        try: st.switch_page("pages/02_Swipe.py")
        except Exception: st.info("Abra **Swipe** no menu.")

st.markdown("</div>", unsafe_allow_html=True)
