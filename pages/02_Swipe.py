import streamlit as st
import json
from pathlib import Path

# ---------- utils ----------
BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def norm_img_path(p):
    return p.replace("\\", "/") if isinstance(p, str) else p

def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def show_image(img_rel: str):
    """Mostra imagem com st.image (caminho relativo) + fallback seguro."""
    img_rel = norm_img_path(img_rel or "")
    if img_rel and not img_rel.startswith("http") and (BASE_DIR / img_rel).exists():
        st.image(img_rel, use_container_width=True)
    elif img_rel.startswith("http"):
        st.image(img_rel, use_container_width=True)
    else:
        st.image("https://via.placeholder.com/800x600.png?text=Investor+Match", use_container_width=True)

# ---------- page ----------
st.set_page_config(page_title="Explorar (Swipe)", page_icon="🔥", layout="centered")

# CSS para simular “tela de celular” e recortar imagem
st.markdown("""
<style>
.app-wrapper { max-width: 420px; margin: 0 auto; }
.app-wrapper .stImage img {
  height: 520px;  /* desktop */
  object-fit: cover;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,.08);
}
@media (max-width: 480px){
  .app-wrapper .stImage img { height: 420px; }
}
.badges span{
  margin-right: 6px; font-size: 12px; padding:3px 8px; border-radius:8px;
  background:#f2f4f7; border:1px solid #e5e7eb;
}
.chip { display:inline-block; padding:4px 10px; margin:4px 6px 0 0; font-size:12px; border:1px solid #eaeaea; border-radius:999px; background:#fafafa; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)
st.markdown("### 🔥 Explorar (Swipe)")

profiles = load_profiles()
if not profiles:
    st.warning("Nenhum perfil disponível ainda.")
else:
    # Exibe UM card por vez (usando índice em session_state)
    st.session_state.setdefault("swipe_idx", 0)
    i = st.session_state["swipe_idx"] % len(profiles)
    card = profiles[i]

    # Imagem (recortada via CSS)
    show_image(card.get("image", ""))

    # badges demo
    st.markdown('<div class="badges"><span>⭐ Pro</span><span>🟢 Online</span></div>', unsafe_allow_html=True)

    st.markdown(f"**{card['name']}**")
    st.caption(f"{card.get('headline','')} • {card.get('location','')}")
    st.write(card.get("bio",""))
    st.markdown("".join([f'<span class="chip">{t}</span>' for t in card.get("tags",[])]), unsafe_allow_html=True)

    # botões com KEYS únicas (evita StreamlitDuplicateElementId)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("❌", use_container_width=True, key=f"pass_{card['id']}"):
            st.session_state["swipe_idx"] += 1
            st.rerun()
    with c2:
        if st.button("💙", use_container_width=True, key=f"like_{card['id']}"):
            st.session_state["swipe_idx"] += 1
            st.rerun()
    with c3:
        if st.button("⭐", use_container_width=True, key=f"super_{card['id']}"):
            st.session_state["swipe_idx"] += 1
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
