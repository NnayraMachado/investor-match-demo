# pages/07_Match.py
import json
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def norm(p): return p.replace("\\","/") if isinstance(p,str) else p

@st.cache_data
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

st.set_page_config(page_title="Match", page_icon="✨", layout="centered")
st.markdown("""
<style>
.app { max-width: 420px; margin: 0 auto; text-align:center; }
.portrait .stImage img { height: 160px; width: 160px; object-fit: cover; border-radius: 16px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app">', unsafe_allow_html=True)
st.markdown("## ✨ Deu Match!")

pid = st.session_state.get("last_match_idx")
name = st.session_state.get("last_match_name", "Investidor")
img_rel = norm(st.session_state.get("last_match_image", ""))

profiles = load_profiles()
if (not img_rel) and pid:
    p = next((x for x in profiles if x.get("id")==pid), None)
    if p:
        name = p.get("name", name)
        img_rel = norm(p.get("image",""))

colA, colB = st.columns(2)
with colA:
    st.markdown('<div class="portrait">', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/360.png?text=Voce", width=160)
    st.caption("Você")
    st.markdown('</div>', unsafe_allow_html=True)
with colB:
    st.markdown('<div class="portrait">', unsafe_allow_html=True)
    if img_rel and not img_rel.startswith("http") and (BASE_DIR / img_rel).exists():
        st.image(img_rel, width=160)
    elif img_rel.startswith("http"):
        st.image(img_rel, width=160)
    else:
        st.image("https://via.placeholder.com/360.png?text=Perfil", width=160)
    st.caption(name)
    st.markdown('</div>', unsafe_allow_html=True)

st.success("Agora vocês podem conversar! 🎉")

c1, c2 = st.columns(2)
with c1:
    if st.button("💬 Ir para Mensagens", use_container_width=True, key="go_msgs"):
        try: st.switch_page("pages/03_Mensagens.py")
        except Exception: st.info("Abra **Mensagens** no menu.")
with c2:
    if st.button("🔙 Voltar ao Swipe", use_container_width=True, key="back_swipe"):
        try: st.switch_page("pages/02_Swipe.py")
        except Exception: st.info("Abra **Swipe** no menu.")

st.markdown("</div>", unsafe_allow_html=True)
