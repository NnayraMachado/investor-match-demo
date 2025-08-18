import streamlit as st
import json, time
from pathlib import Path

# -------- utils ----------
BASE_DIR = Path(__file__).resolve().parent
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # defaults para demo
        for p in data:
            p.setdefault("type", "investor")  # investor|startup
            p.setdefault("icon", "💰" if p["type"] == "investor" else "🚀")
            p.setdefault("lat", None); p.setdefault("lon", None)
            p.setdefault("stage", "Seed")              # startup
            p.setdefault("raising", 1500)              # em mil USD (ex.: 1500 = US$1,5M)
            p.setdefault("ticket_min", 100)           # investor
            p.setdefault("ticket_max", 2000)
            p.setdefault("verified", True)
        return data
    return []

def profile_icon(p):
    return p.get("icon") or ("💰" if p.get("type") == "investor" else "🚀")

# -------- page ----------
st.set_page_config(page_title="Investor Match", page_icon="💼", layout="centered")

# CSS global
st.markdown("""
<style>
.home-wrapper { max-width: 960px; margin: 0 auto; }
.app-wrapper  { max-width: 420px; margin: 0 auto; }

/* “avatar” redondo com ícone */
.pfp { width: 120px; height: 120px; border-radius: 50%;
       background: #f1f5f9; display:flex; align-items:center; justify-content:center;
       box-shadow: 0 6px 16px rgba(0,0,0,.06); margin: 6px 0 10px; }
.pfp span { font-size: 56px; line-height: 1; }

.badges span, .chip {
  font-size: 12px; padding: 4px 10px; border-radius: 999px;
  background: #f7f8fa; border: 1px solid #edf0f2; margin-right: 6px;
}
.small { color:#6b7280; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# estado global útil
st.session_state.setdefault("user_plan", st.session_state.get("user_plan","Free"))
st.session_state.setdefault("likes_used", 0)
st.session_state.setdefault("likes_reset_at", time.time()+3600)
st.session_state.setdefault("boost_left", 1 if st.session_state["user_plan"]=="Pro" else 0)

# sidebar
st.sidebar.title("Menu")
st.sidebar.page_link("app.py", label="app")
st.sidebar.page_link("pages/00_Apresentacao.py", label="Apresentacao")
st.sidebar.page_link("pages/01_Perfil.py", label="Perfil")
st.sidebar.page_link("pages/02_Swipe.py", label="Swipe")
st.sidebar.page_link("pages/03_Mensagens.py", label="Mensagens")
st.sidebar.page_link("pages/04_Assinatura.py", label="Assinatura")
st.sidebar.page_link("pages/05_Admin_Demo.py", label="Admin")
st.sidebar.page_link("pages/06_Feed.py", label="Feed")
st.sidebar.page_link("pages/07_Match.py", label="Match")
st.sidebar.page_link("pages/08_Tendencias.py", label="Tendencias")
st.sidebar.page_link("pages/09_Dealroom.py", label="Dealroom")
st.sidebar.page_link("pages/10_Ranking.py", label="Ranking")
st.sidebar.page_link("pages/11_Eventos.py", label="Eventos")
st.sidebar.page_link("pages/12_Recomendacoes.py", label="Recomendacoes")

st.title("💼 Investor Match")
st.caption("Conectando investidores e startups de forma inteligente.")

profiles = load_profiles()

st.markdown('<div class="home-wrapper">', unsafe_allow_html=True)
st.subheader("Perfis em destaque")

if profiles:
    for p in profiles[:4]:
        icon = profile_icon(p)
        st.markdown(f'<div class="pfp"><span>{icon}</span></div>', unsafe_allow_html=True)
        v_badge = " <span class='small'>🛡️ Verificado</span>" if p.get("verified") else ""
        st.markdown(f"**{p['name']}**{v_badge}", unsafe_allow_html=True)
        st.caption(f"{p.get('headline','')} • {p.get('city', p.get('location',''))}")
        st.write(p.get("bio",""))
        st.divider()
else:
    st.info("Sem perfis para exibir ainda.")

st.markdown("</div>", unsafe_allow_html=True)
