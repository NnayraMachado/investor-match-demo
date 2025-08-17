import streamlit as st
import json
from pathlib import Path

# --- Função utilitária para normalizar caminhos ---
def norm_img_path(p):
    return p.replace("\\", "/") if isinstance(p, str) else p

# --- Caminhos base ---
BASE_DIR = Path(__file__).resolve().parent.parent
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

# --- Funções auxiliares ---
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- Página Swipe ---
st.set_page_config(page_title="Explorar (Swipe)", page_icon="🔥", layout="wide")

st.title("🔥 Explorar (Swipe)")

profiles = load_profiles()
if not profiles:
    st.warning("Nenhum perfil disponível ainda.")
else:
    for card in profiles:
        with st.container():
            img_path = norm_img_path(card.get("image", ""))
            pobj = BASE_DIR / img_path if img_path and not img_path.startswith("http") else None
            if pobj and pobj.exists():
                st.image(str(pobj), use_container_width=True)
            else:
                st.image("https://via.placeholder.com/800x600.png?text=Investor+Match", use_container_width=True)

            st.subheader(f"{card['name']} — {card['headline']}")
            st.caption(f"{card['location']}")
            st.write(card.get("bio", ""))
            st.markdown("**Tags:** " + ", ".join(card.get("tags", [])))
            st.divider()
