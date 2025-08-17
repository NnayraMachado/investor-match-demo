# pages/02_Swipe.py
import json
from pathlib import Path
from secrets import randbelow
import streamlit as st

# ---------- paths / data ----------
BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def norm_img_path(p):
    return p.replace("\\", "/") if isinstance(p, str) else p

@st.cache_data
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # seed de pitch para os 2 primeiros (se não tiver)
        for i, p in enumerate(data[:2], start=1):
            p.setdefault("pitch_url", "https://www.youtube.com/embed/jfKfPfyJRdk")
        for p in data[2:]:
            p.setdefault("pitch_url", None)
        return data
    return []

profiles = load_profiles()

# ---------- estado ----------
st.session_state.setdefault("swipe_idx", 0)
st.session_state.setdefault("matches", set())
st.session_state.setdefault("liked", set())
st.session_state.setdefault("passed", set())
st.session_state.setdefault("my_tags", ["SaaS", "Fintech"])

# like recíproco (estável por perfil)
def they_like_back(profile_id: int) -> bool:
    key = f"likeback_{profile_id}"
    if key not in st.session_state:
        st.session_state[key] = randbelow(100) < 30  # 30% chance
    return st.session_state[key]

# ---------- page ----------
st.set_page_config(page_title="Explorar (Swipe)", page_icon="🔥", layout="centered")

# CSS: wrapper tipo celular + imagem menor
st.markdown("""
<style>
.app-wrapper { max-width: 420px; margin: 0 auto; }
.app-wrapper .stImage img {
  height: 300px;              /* <= fica menor */
  object-fit: cover;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,.08);
}
@media (max-width: 480px){
  .app-wrapper .stImage img { height: 300px; }
}
.badges span{
  margin-right: 6px; font-size: 12px; padding:3px 8px; border-radius:8px;
  background:#f2f4f7; border:1px solid #e5e7eb;
}
.chip { display:inline-block; padding:4px 10px; margin:4px 6px 0 0; font-size:12px;
  border:1px solid #eaeaea; border-radius:999px; background:#fafafa; }
.meta { color:#6b7280; font-size:13px; margin-top:-4px; }
.comp-wrap { margin: 6px 0 4px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)
st.markdown("### 🔥 Explorar (Swipe)")

if not profiles:
    st.warning("Nenhum perfil disponível ainda.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ----- card atual -----
i = st.session_state["swipe_idx"] % len(profiles)
card = profiles[i]

# imagem (com normalização e fallback)
img_rel = norm_img_path(card.get("image", ""))
if img_rel and not img_rel.startswith("http") and (BASE_DIR / img_rel).exists():
    st.image(img_rel, use_container_width=True)
elif img_rel.startswith("http"):
    st.image(img_rel, use_container_width=True)
else:
    st.image("https://via.placeholder.com/800x600.png?text=Investor+Match", use_container_width=True)

# badges demo
st.markdown('<div class="badges"><span>⭐ Pro</span><span>🟢 Online</span></div>', unsafe_allow_html=True)

# nome, localização (com fallback seguro)
st.markdown(f"**{card.get('name','')}**")
headline = card.get("headline", "")
loc = card.get("location", "")
city = card.get("city") or (loc.split(",")[0].strip() if "," in loc else loc)
state = card.get("state") or (loc.split(",")[1].strip() if "," in loc else "")
country = card.get("country") or "Brasil"
st.markdown(f'<div class="meta">{headline} • {city}{(", " + state) if state else ""} • {country}</div>', unsafe_allow_html=True)

# compatibilidade (%)
my_tags = set(t.lower() for t in st.session_state.get("my_tags", []))
their = set(t.lower() for t in card.get("tags", []))
jacc = 0 if not (my_tags | their) else round(100 * len(my_tags & their) / len(my_tags | their))
st.markdown(f'<div class="comp-wrap">Compatibilidade: <b>{jacc}%</b></div>', unsafe_allow_html=True)
st.progress(jacc)

# pitch curto (opcional)
if card.get("pitch_url"):
    if st.checkbox("▶️ Ver pitch (1 min)", key=f"pitch_{card.get('id', i)}"):
        st.video(card["pitch_url"])

# bio + chips
st.write(card.get("bio", ""))
st.markdown("".join([f'<span class="chip">{t}</span>' for t in card.get("tags", [])]), unsafe_allow_html=True)

# ----- botões (keys únicas) -----
c1, c2, c3 = st.columns(3)
pid = card.get("id", i)

with c1:
    if st.button("❌", use_container_width=True, key=f"pass_{pid}"):
        st.session_state["passed"].add(pid)
        st.session_state["swipe_idx"] += 1
        st.rerun()

with c2:
    if st.button("💙", use_container_width=True, key=f"like_{pid}"):
        st.session_state["liked"].add(pid)
        if they_like_back(pid):
            # virou match!
            st.session_state["matches"].add(pid)
            st.session_state["last_match_idx"] = pid
            st.session_state["last_match_name"] = card.get("name","")
            st.session_state["last_match_image"] = img_rel
            try:
                st.switch_page("pages/07_Match.py")
            except Exception:
                st.success("É um match! (demo)")
        else:
            st.session_state["swipe_idx"] += 1
            st.rerun()

with c3:
    if st.button("⭐", use_container_width=True, key=f"super_{pid}"):
        st.session_state["liked"].add(pid)
        st.session_state["matches"].add(pid)
        st.session_state["last_match_idx"] = pid
        st.session_state["last_match_name"] = card.get("name","")
        st.session_state["last_match_image"] = img_rel
        try:
            st.switch_page("pages/07_Match.py")
        except Exception:
            st.success("É um match! (Super Like demo)")

st.markdown("---")
if st.button("💥 Forçar Match (demo)", key=f"force_{pid}"):
    st.session_state["matches"].add(pid)
    st.session_state["last_match_idx"] = pid
    st.session_state["last_match_name"] = card.get("name","")
    st.session_state["last_match_image"] = img_rel
    try:
        st.switch_page("pages/07_Match.py")
    except Exception:
        st.success("É um match! (forçado)")

st.markdown("</div>", unsafe_allow_html=True)

