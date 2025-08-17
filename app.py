import streamlit as st
import json
from pathlib import Path

# ---------- utils ----------
def norm_img_path(p):
    return p.replace("\\", "/") if isinstance(p, str) else p

BASE_DIR = Path(__file__).resolve().parent
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ---------- page ----------
st.set_page_config(page_title="Investor Match", page_icon="💼", layout="wide")

# CSS global: container central compacto e cards com imagem recortada
st.markdown("""
<style>
/* largura tipo celular para páginas que usam .app-wrapper */
.app-wrapper { max-width: 420px; margin: 0 auto; }
.home-wrapper { max-width: 960px; margin: 0 auto; }

/* imagem de destaque na home */
.card-img {
  width: 100%;
  height: 360px;          /* evita ficar gigante */
  object-fit: cover;
  border-radius: 14px;
  display: block;
}
@media (max-width: 480px){
  .card-img { height: 260px; }
}
.section-title { margin: 6px 0 2px 0; font-weight: 700; }
.badges span{
  margin-right: 6px; font-size: 12px; padding:3px 8px; border-radius:8px;
  background:#f2f4f7; border:1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

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

with st.container():
    st.markdown('<div class="home-wrapper">', unsafe_allow_html=True)

    st.subheader("Perfis em destaque")
    if profiles:
        for p in profiles[:2]:
            img_rel = norm_img_path(p.get("image",""))
            # tenta caminho relativo no repo
            path = BASE_DIR / img_rel if img_rel and not img_rel.startswith("http") else None
            if path and path.exists():
                st.markdown(f'<img src="{path.as_posix()}" class="card-img">', unsafe_allow_html=True)
            else:
                # placeholder seguro
                st.markdown('<img src="https://via.placeholder.com/800x600.png?text=Investor+Match" class="card-img">', unsafe_allow_html=True)

            st.markdown(f"**{p['name']}**")
            st.caption(f"{p['headline']} • {p.get('location','')}")
            st.write(p.get("bio",""))
            st.divider()
    else:
        st.info("Sem perfis para exibir ainda.")

    st.markdown("</div>", unsafe_allow_html=True)
