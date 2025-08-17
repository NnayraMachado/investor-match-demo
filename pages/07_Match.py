# pages/07_Match.py
import json
from pathlib import Path
import streamlit as st

# ---------- utils ----------
BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def norm_img_path(p):
    return p.replace("\\", "/") if isinstance(p, str) else p

@st.cache_data
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def show_image(img_rel: str, width: int = 180):
    """Mostra imagem (local/URL) com fallback."""
    img_rel = norm_img_path(img_rel or "")
    if img_rel and not img_rel.startswith("http") and (BASE_DIR / img_rel).exists():
        st.image(img_rel, width=width)
    elif img_rel.startswith("http"):
        st.image(img_rel, width=width)
    else:
        st.image("https://via.placeholder.com/360.png?text=Investor", width=width)

# ---------- page ----------
st.set_page_config(page_title="Match", page_icon="✨", layout="centered")

# CSS para fotos pequenas e redondas
st.markdown("""
<style>
.app-wrapper { max-width: 420px; margin: 0 auto; text-align:center; }
.smallpic img{ height: 180px; width: 180px; object-fit: cover; border-radius: 16px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)
st.markdown("## ✨ Deu Match!")

# Recupera info do último match (preenchida na tela de Swipe)
profiles = load_profiles()
pid = st.session_state.get("last_match_idx")
name = st.session_state.get("last_match_name", "Outro investidor")
img_rel = st.session_state.get("last_match_image", "")

# fallback: se veio só o id, procure no JSON
if not img_rel and pid:
    p = next((x for x in profiles if x.get("id")==pid), None)
    if p: 
        name = p.get("name", name)
        img_rel = p.get("image", img_rel)

c1, c2, c3 = st.columns([1,2,1])
with c2:
    st.write("Você", name)

cA, cB = st.columns(2)
with cA:
    st.markdown('<div class="smallpic">', unsafe_allow_html=True)
    # sua foto (placeholder mesmo)
    st.image("https://via.placeholder.com/360.png?text=Voce", width=180)
    st.caption("Você")
    st.markdown('</div>', unsafe_allow_html=True)

with cB:
    st.markdown('<div class="smallpic">', unsafe_allow_html=True)
    show_image(img_rel, width=180)
    st.caption(name)
    st.markdown('</div>', unsafe_allow_html=True)

st.success("Agora vocês podem conversar! 🎉")

col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Ir para Mensagens", use_container_width=True, key="go_msgs"):
        try:
            st.switch_page("pages/03_Mensagens.py")
        except Exception:
            st.info("Abra a página **Mensagens** no menu.")
with col2:
    if st.button("🔙 Voltar ao Swipe", use_container_width=True, key="back_swipe"):
        try:
            st.switch_page("pages/02_Swipe.py")
        except Exception:
            st.info("Abra a página **Swipe** no menu.")

st.markdown("</div>", unsafe_allow_html=True)
