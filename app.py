import streamlit as st
import json
from pathlib import Path

# --- Função utilitária para normalizar caminhos ---
def norm_img_path(p):
    return p.replace("\\", "/") if isinstance(p, str) else p

# --- Caminhos base ---
BASE_DIR = Path(__file__).resolve().parent
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

# --- Funções auxiliares ---
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_profiles(data):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- Configuração da página ---
st.set_page_config(page_title="Investor Match", page_icon="💼", layout="wide")

# --- Menu lateral ---
st.sidebar.title("Menu")
menu = st.sidebar.radio("Navegação", ["Apresentacao", "Perfil", "Swipe", "Mensagens", "Assinatura", "Admin Demo", "Match", "Tendencias"])

# --- Páginas ---
if menu == "Apresentacao":
    st.title("💼 Investor Match")
    st.markdown("Conectando investidores e startups de forma inteligente.")
    st.image("https://via.placeholder.com/1200x400.png?text=Investor+Match+Demo", use_container_width=True)

    st.header("🚀 Recursos principais")
    st.markdown("""
    - Swipe para descobrir novos investidores e startups
    - Chat integrado
    - Área de matches confirmados
    - Dashboard de tendências
    """)

    # Destaques
    st.subheader("✨ Perfis em destaque")
    profiles = load_profiles()
    if profiles:
        for p in profiles[:3]:
            img_path = norm_img_path(p.get("image", ""))
            pobj = BASE_DIR / img_path if img_path and not img_path.startswith("http") else None
            if pobj and pobj.exists():
                st.image(str(pobj), use_container_width=True)
            else:
                st.image("https://via.placeholder.com/800x600.png?text=Investor+Match", use_container_width=True)
            st.write(f"**{p['name']}** — {p['headline']} ({p['location']})")
            st.caption(", ".join(p["tags"]))

elif menu == "Perfil":
    st.title("👤 Meu Perfil")
    st.info("Aqui o usuário poderá editar informações do perfil.")

elif menu == "Mensagens":
    st.title("💬 Mensagens")
    st.info("Chat em tempo real entre investidores e startups.")

elif menu == "Assinatura":
    st.title("💳 Assinatura Pro")
    st.info("Página para planos pagos, upgrades e billing.")

elif menu == "Admin Demo":
    st.title("⚙️ Admin Demo")
    st.info("Apenas administradores conseguem visualizar dados completos.")

elif menu == "Match":
    st.title("❤️ Matches confirmados")
    st.info("Lista de conexões entre investidores e startups.")

elif menu == "Tendencias":
    st.title("📊 Tendências do mercado")
    st.info("Análises e insights do ecossistema.")
