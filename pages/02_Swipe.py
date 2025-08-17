import streamlit as st
import json
from pathlib import Path

# ---------- utils ----------
def norm_img_path(p):
    return p.replace("\\", "/") if isinstance(p, str) else p

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ---------- page ----------
st.set_page_config(page_title="Explorar (Swipe)", page_icon="🔥", layout="wide")

# CSS para simular “tela de celular” e cortar a imagem
st.markdown("""
<style>
.app-wrapper { max-width: 420px; margin: 0 auto; }
.phone-img {
  width: 100%;
  height: 520px;           /* altura fixa no desktop p/ não ficar gigante */
  object-fit: cover;
  border-radius: 16px;
  display: block;
  box-shadow: 0 8px 24px rgba(0,0,0,.08);
}
@media (max-width: 480px){
  .phone-img { height: 420px; }
}
.title-row { display:flex; align-items:center; gap:10px; }
.badges span{
  margin-right: 6px; font-size: 12px; padding:3px 8px; border-radius:8px;
  background:#f2f4f7; border:1px solid #e5e7eb;
}
.chip { display:inline-block; padding:4px 10px; margin:4px 6px 0 0; font-size:12px; border:1px solid #eaeaea; border-radius:999px; background:#fafafa; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)

st.markdown('<div class="title-row"><span style="font-size:26px">🔥</span><h2 style="margin:0">Explorar (Swipe)</h2></div>', unsafe_allow_html=True)

profiles = load_profiles()
if not profiles:
    st.warning("Nenhum perfil disponível ainda.")
else:
    # mostra um por vez (estático/compacto — você pode plugar seu estado de índice se quiser)
    for card in profiles:
        img_rel = norm_img_path(card.get("image",""))
        path = BASE_DIR / img_rel if img_rel and not img_rel.startswith("http") else None
        if path and path.exists():
            st.markdown(f'<img src="{path.as_posix()}" class="phone-img">', unsafe_allow_html=True)
        else:
            st.markdown('<img src="https://via.placeholder.com/800x600.png?text=Investor+Match" class="phone-img">', unsafe_allow_html=True)

        # badges simples (exemplo)
        st.markdown('<div class="badges"><span>⭐ Pro</span><span>🟢 Online</span></div>', unsafe_allow_html=True)

        st.markdown(f"**{card['name']}**")
        st.caption(f"{card['headline']} • {card.get('location','')}")
        st.write(card.get("bio",""))
        st.markdown("".join([f'<span class="chip">{t}</span>' for t in card.get("tags",[])]), unsafe_allow_html=True)

        # botões demo (apenas layout)
        c1, c2, c3 = st.columns(3)
        with c1: st.button("❌", use_container_width=True)
        with c2: st.button("💙", use_container_width=True)
        with c3: st.button("⭐", use_container_width=True)

        st.divider()

st.markdown("</div>", unsafe_allow_html=True)
