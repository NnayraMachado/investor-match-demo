# pages/02_Swipe.py
import json, math, random
from pathlib import Path
from secrets import randbelow
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for i, p in enumerate(data[:2], start=1):
            p.setdefault("pitch_url", "https://www.youtube.com/embed/jfKfPfyJRdk")
        for p in data:
            p.setdefault("pitch_url", None)
            p.setdefault("type", "investor")
            p.setdefault("icon", "💰" if p["type"] == "investor" else "🚀")
            p.setdefault("lat", None)
            p.setdefault("lon", None)
        return data
    return []

def profile_icon(p):
    return p.get("icon") or ("💰" if p.get("type") == "investor" else "🚀")

profiles = load_profiles()

# ---------- estado ----------
st.session_state.setdefault("swipe_idx", 0)
st.session_state.setdefault("matches", set())
st.session_state.setdefault("liked", set())
st.session_state.setdefault("passed", set())
st.session_state.setdefault("history", [])
st.session_state.setdefault("my_tags", ["SaaS", "Fintech"])
st.session_state.setdefault("user_plan", st.session_state.get("user_plan","Free"))

# localização do usuário (01_Perfil atualiza real)
st.session_state.setdefault("my_lat", -23.5505)
st.session_state.setdefault("my_lon", -46.6333)

def they_like_back(profile_id: int) -> bool:
    key = f"likeback_{profile_id}"
    if key not in st.session_state:
        st.session_state[key] = randbelow(100) < 30
    return st.session_state[key]

# distância
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def distance_label(p: dict) -> str:
    my_lat = st.session_state.get("my_lat")
    my_lon = st.session_state.get("my_lon")
    lat2, lon2 = p.get("lat"), p.get("lon")
    if None not in (my_lat, my_lon, lat2, lon2):
        km = haversine_km(my_lat, my_lon, lat2, lon2)
        return f"~{int(round(km))} km de você"
    rnd = random.Random(p.get("id",0))
    return f"~{rnd.randint(1,25)} km de você"

# ---------- page ----------
st.set_page_config(page_title="Explorar (Swipe)", page_icon="🔥", layout="centered")

st.markdown("""
<style>
.app-wrapper { max-width: 420px; margin: 0 auto; }

/* bloco grande do ícone (substitui a foto) */
.card-icon { width: 100%; height: 220px; border-radius: 16px;
             background: linear-gradient(180deg, #f1f5f9, #e2e8f0);
             display:flex; align-items:center; justify-content:center;
             box-shadow: 0 8px 24px rgba(0,0,0,.08); margin-bottom:8px; }
.card-icon span { font-size: 110px; line-height: 1; }

.badges span{
  margin-right: 6px; font-size: 12px; padding:3px 8px; border-radius:8px;
  background:#f2f4f7; border:1px solid #e5e7eb;
}
.chip { display:inline-block; padding:4px 10px; margin:4px 6px 0 0; font-size:12px;
  border:1px solid #eaeaea; border-radius:999px; background:#fafafa; }
.meta, .distance { color:#6b7280; font-size:13px; }
.comp-wrap { margin: 6px 0 4px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)
st.markdown("### 🔥 Explorar (Swipe)")

if not profiles:
    st.info("Sem perfis por enquanto.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ----- card atual -----
idx = st.session_state["swipe_idx"] % len(profiles)
p = profiles[idx]
pid = p.get("id", idx)

# ÍCONE no lugar da foto
st.markdown(f'<div class="card-icon"><span>{profile_icon(p)}</span></div>', unsafe_allow_html=True)

# badges
st.markdown('<div class="badges"><span>⭐ Pro</span><span>🟢 Online</span></div>', unsafe_allow_html=True)

# título + meta
headline = p.get("headline", "")
loc = p.get("location", "")
city = p.get("city") or (loc.split(",")[0].strip() if "," in loc else loc)
state = p.get("state") or (loc.split(",")[1].strip() if "," in loc else "")
country = p.get("country") or "Brasil"

st.markdown(f"**{profile_icon(p)} {p.get('name','')}**")
st.markdown(f'<div class="meta">{headline} • {city}{(", " + state) if state else ""} • {country}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="distance">{distance_label(p)}</div>', unsafe_allow_html=True)

# compatibilidade
my = set(t.lower() for t in st.session_state.get("my_tags", []))
their = set(t.lower() for t in p.get("tags", []))
jacc = 0 if not (my | their) else round(100 * len(my & their) / len(my | their))
st.markdown(f'<div class="comp-wrap">Compatibilidade: <b>{jacc}%</b></div>', unsafe_allow_html=True)
st.progress(jacc)

# pitch (toggle)
if p.get("pitch_url"):
    if st.checkbox("▶️ Ver pitch (1 min)", key=f"pitch_{pid}"):
        st.video(p["pitch_url"])

# bio + tags
st.write(p.get("bio", ""))
st.markdown("".join([f'<span class="chip">{t}</span>' for t in p.get("tags", [])]), unsafe_allow_html=True)

# ----- ações -----
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("❌", use_container_width=True, key=f"pass_{pid}"):
        st.session_state["history"].append(idx)
        st.session_state["passed"].add(pid)
        st.session_state["swipe_idx"] += 1
        st.rerun()
with c2:
    if st.button("💙", use_container_width=True, key=f"like_{pid}"):
        st.session_state["history"].append(idx)
        st.session_state["liked"].add(pid)
        if they_like_back(pid):
            st.session_state["matches"].add(pid)
            st.session_state["last_match_idx"] = pid
            st.session_state["last_match_name"] = p.get("name","")
            st.session_state["last_match_image"] = ""  # não usamos mais foto
            try:
                st.switch_page("pages/07_Match.py")
            except Exception:
                st.success("É um match! (demo)")
        else:
            st.session_state["swipe_idx"] += 1
            st.rerun()
with c3:
    if st.button("⭐", use_container_width=True, key=f"super_{pid}"):
        st.session_state["history"].append(idx)
        st.session_state["liked"].add(pid)
        st.session_state["matches"].add(pid)
        st.session_state["last_match_idx"] = pid
        st.session_state["last_match_name"] = p.get("name","")
        st.session_state["last_match_image"] = ""
        try:
            st.switch_page("pages/07_Match.py")
        except Exception:
            st.success("É um match! (Super Like demo)")

st.markdown("---")

# Rewind (Pro)
if st.session_state.get("user_plan") == "Pro":
    if st.button("⤺ Rewind (Pro) — desfazer último swipe", use_container_width=True):
        if st.session_state["history"]:
            prev_idx = st.session_state["history"].pop()
            st.session_state["swipe_idx"] = prev_idx
            st.success("Última ação desfeita (demo).")
            st.rerun()
        else:
            st.info("Nada para desfazer ainda.")

if st.button("💥 Forçar Match (demo)", key=f"force_{pid}"):
    st.session_state["matches"].add(pid)
    st.session_state["last_match_idx"] = pid
    st.session_state["last_match_name"] = p.get("name","")
    st.session_state["last_match_image"] = ""
    try:
        st.switch_page("pages/07_Match.py")
    except Exception:
        st.success("É um match! (forçado)")

st.markdown("</div>", unsafe_allow_html=True)
