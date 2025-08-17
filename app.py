import streamlit as st
import json
from pathlib import Path

# -------- utils ----------
BASE_DIR = Path(__file__).resolve().parent
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def norm_img_path(p):
    return p.replace("\\", "/") if isinstance(p, str) else p

def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def show_image(img_rel: str, height: int = 360):
    """Mostra imagem local/URL com fallback e recorte (object-fit: cover via CSS)."""
    img_rel = norm_img_path(img_rel or "")
    # Usaremos st.image com caminho RELATIVO (repo root)
    if img_rel and not img_rel.startswith("http") and (BASE_DIR / img_rel).exists():
        st.image(img_rel, use_container_width=True)
    elif img_rel.startswith("http"):
        st.image(img_rel, use_container_width=True)
    else:
        st.image("https://via.placeholder.com/800x600.png?text=Investor+Match", use_container_width=True)

# -------- page ----------
st.set_page_config(page_title="Investor Match", page_icon="💼", layout="centered")

# CSS global: containers compactos e imagem recortada
st.markdown("""
<style>
.home-wrapper { max-width: 960px; margin: 0 auto; }
.app-wrapper  { max-width: 420px; margin: 0 auto; }
.home-wrapper .stImage img,
.app-wrapper  .stImage img {
  height: 360px;
  object-fit: cover;
  border-radius: 14px;
}
@media (max-width: 480px){
  .home-wrapper .stImage img,
  .app-wrapper  .stImage img { height: 260px; }
}
.badges span{
  margin-right: 6px; font-size: 12px; padding:3px 8px; border-radius:8px;
  background:#f2f4f7; border:1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# sidebar de navegação (demo)
st.sidebar.title("Menu")
st.sidebar.page_link("app.py", label="app")
st.sidebar.page_link("pages/00_Apresentacao.py", label="Apresentacao")
st.sidebar.page_link("pages/01_Perfil.py", label="Perfil")
st.sidebar.page_link("pages/02_Swipe.py", label="Swipe")
st.sidebar.page_link("pages/03_Mensagens.py", label="Mensagens")
st.sidebar.page_link("pages/04_Assinatura.py", label="Assinatura")
st.sidebar.page_link("pages/05_Admin_Demo.py", label="Admin Demo")
st.sidebar.page_link("pages/07_Match.py", label="Match")
st.sidebar.page_link("pages/08_Tendencias.py", label="Tendencias")

st.title("💼 Investor Match")
st.caption("Conectando investidores e startups de forma inteligente.")

profiles = load_profiles()

st.markdown('<div class="home-wrapper">', unsafe_allow_html=True)
st.subheader("Perfis em destaque")

if profiles:
    for p in profiles[:2]:
        show_image(p.get("image", ""))           # ✅ st.image com fallback
        st.markdown(f"**{p['name']}**")
        st.caption(f"{p.get('headline','')} • {p.get('location','')}")
        st.write(p.get("bio",""))
        st.divider()
else:
    st.info("Sem perfis para exibir ainda.")

st.markdown("</div>", unsafe_allow_html=True)
