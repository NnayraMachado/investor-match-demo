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
            data = json.load(f)
        # defaults (para demo)
        for p in data:
            if "type" not in p:
                p["type"] = "investor"
            if "icon" not in p:
                p["icon"] = "💰" if p["type"] == "investor" else "🚀"
        return data
    return []

def show_image(img_rel: str):
    """Mostra imagem local/URL com fallback (recorte via CSS .card-img)."""
    img_rel = norm_img_path(img_rel or "")
    if img_rel and not img_rel.startswith("http") and (BASE_DIR / img_rel).exists():
        st.image(img_rel, use_container_width=True)
    elif img_rel.startswith("http"):
        st.image(img_rel, use_container_width=True)
    else:
        st.image("https://via.placeholder.com/800x600.png?text=Investor+Match", use_container_width=True)

# -------- page ----------
st.set_page_config(page_title="Investor Match", page_icon="💼", layout="centered")

# CSS global
st.markdown("""
<style>
/* largura tipo "mobile" */
.home-wrapper { max-width: 960px; margin: 0 auto; }
.app-wrapper  { max-width: 420px; margin: 0 auto; }

/* imagens padronizadas para cards */
.card-img img {
  width: 100% !important;
  height: 260px !important;
  object-fit: cover;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,.06);
}

/* avatar compacto */
.avatar img {
  width: 88px !important;
  height: 88px !important;
  object-fit: cover;
  border-radius: 12px;
}

/* chips/badges */
.badges span, .chip {
  font-size: 12px; padding: 4px 10px; border-radius: 999px;
  background: #f7f8fa; border: 1px solid #edf0f2; margin-right: 6px;
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
st.sidebar.page_link("pages/06_Feed.py", label="Feed")
st.sidebar.page_link("pages/07_Match.py", label="Match")
st.sidebar.page_link("pages/08_Tendencias.py", label="Tendencias")

st.title("💼 Investor Match")
st.caption("Conectando investidores e startups de forma inteligente.")

profiles = load_profiles()

st.markdown('<div class="home-wrapper">', unsafe_allow_html=True)
st.subheader("Perfis em destaque")

if profiles:
    for p in profiles[:2]:
        st.markdown('<div class="card-img">', unsafe_allow_html=True)
        show_image(p.get("image", ""))
        st.markdown('</div>', unsafe_allow_html=True)
        icon = p.get("icon", "💰")
        st.markdown(f"**{icon} {p['name']}**")
        st.caption(f"{p.get('headline','')} • {p.get('location', p.get('city',''))}")
        st.write(p.get("bio",""))
        st.divider()
else:
    st.info("Sem perfis para exibir ainda.")

st.markdown("</div>", unsafe_allow_html=True)
