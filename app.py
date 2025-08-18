import streamlit as st
import json
from pathlib import Path

# -------- utils ----------
BASE_DIR = Path(__file__).resolve().parent
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for p in data:
            p.setdefault("type", "investor")
            p.setdefault("icon", "💰" if p["type"] == "investor" else "🚀")
        return data
    return []

def profile_icon(p):
    return p.get("icon") or ("💰" if p.get("type") == "investor" else "🚀")

# -------- page ----------
st.set_page_config(page_title="Investor Match", page_icon="💼", layout="centered")

# CSS global (ícones no lugar de fotos)
st.markdown("""
<style>
.home-wrapper { max-width: 960px; margin: 0 auto; }
.app-wrapper  { max_width: 420px; margin: 0 auto; }

/* “avatar” redondo com ícone */
.pfp { width: 120px; height: 120px; border-radius: 50%;
       background: #f1f5f9; display:flex; align-items:center; justify-content:center;
       box-shadow: 0 6px 16px rgba(0,0,0,.06); margin: 6px 0 10px; }
.pfp span { font-size: 56px; line-height: 1; }

.badges span, .chip {
  font-size: 12px; padding: 4px 10px; border-radius: 999px;
  background: #f7f8fa; border: 1px solid #edf0f2; margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

# sidebar
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
    for p in profiles[:4]:
        icon = profile_icon(p)
        st.markdown(f'<div class="pfp"><span>{icon}</span></div>', unsafe_allow_html=True)
        st.markdown(f"**{p['name']}**")
        st.caption(f"{p.get('headline','')} • {p.get('location', p.get('city',''))}")
        st.write(p.get("bio",""))
        st.divider()
else:
    st.info("Sem perfis para exibir ainda.")

st.markdown("</div>", unsafe_allow_html=True)
