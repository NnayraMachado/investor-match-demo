import streamlit as st
import json, math, random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

@st.cache_data
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for p in data:
            p.setdefault("type", "investor")
            p.setdefault("icon", "💰" if p["type"] == "investor" else "🚀")
            p.setdefault("tags", p.get("tags",["SaaS"]))
            p.setdefault("stage","Seed")
            p.setdefault("raising", 1500)
        return data
    return []

def icon_of(p): 
    return p.get("icon","💰" if p.get("type")=="investor" else "🚀")

# --- compatibilidade (mesma base do Swipe) ---
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    import math as m
    phi1, phi2 = m.radians(lat1), m.radians(lat2)
    dphi = m.radians(lat2 - lat1)
    dl = m.radians(lon2 - lon1)
    a = m.sin(dphi/2)**2 + m.cos(phi1)*m.cos(phi2)*m.sin(dl/2)**2
    c = 2*m.atan2(m.sqrt(a), m.sqrt(1-a))
    return R * c

def distance_km(my_lat, my_lon, p):
    lat2, lon2 = p.get("lat"), p.get("lon")
    if None not in (my_lat, my_lon, lat2, lon2):
        return int(round(haversine_km(my_lat, my_lon, lat2, lon2)))
    rnd = random.Random(p.get("id",0)); return rnd.randint(1,25)

def compat_breakdown(p, st_state):
    my_tags = set(t.lower() for t in st_state.get("my_tags", []))
    their_tags = set(t.lower() for t in p.get("tags", []))
    jacc = (100 * len(my_tags & their_tags) / max(1, len(my_tags | their_tags)))

    my_stage = st_state.get("my_stage","Seed")
    stg = p.get("stage","Seed")
    if st_state.get("my_type","investor") == "investor":
        stage_fit = 100 if stg in ["Pre-Seed","Seed","Series A"] else 80
    else:
        stage_fit = 100 if stg == my_stage else (70 if (my_stage,stg) in [("Pre-Seed","Seed"),("Seed","Pre-Seed"),("Seed","Series A")] else 50)

    raising = p.get("raising",1500)
    tmin = st_state.get("my_ticket_min", 100)
    tmax = st_state.get("my_ticket_max", 2000)
    if tmin <= raising <= tmax:
        ticket_fit = 100
    else:
        diff = min(abs(raising - (tmax if raising>tmax else tmin)), 4000)
        ticket_fit = max(0, 100 - diff*0.04)

    dist = distance_km(st_state.get("my_lat",-23.55), st_state.get("my_lon",-46.63), p)
    dist_fit = 100 if dist <= 20 else (85 if dist <= 100 else (65 if dist <= 300 else 45))

    score = round(0.4*jacc + 0.3*stage_fit + 0.2*ticket_fit + 0.1*dist_fit)
    return score, {"Tags": round(jacc), "Estágio": round(stage_fit), "Ticket": round(ticket_fit), "Distância": round(dist_fit)}, dist

st.set_page_config(page_title="Recomendações", page_icon="✨", layout="centered")
st.title("✨ Recomendações inteligentes")

if st.session_state.get("user_plan")!="Pro":
    st.warning("🔒 As recomendações avançadas fazem parte do **Pro**.")
    st.stop()

profiles = load_profiles()
my_type = st.session_state.get("my_type","investor")

# Ordena por score (com pitada de diversidade)
def rec_score(p):
    score, _, _ = compat_breakdown(p, st.session_state)
    # adiciona uma leve aleatoriedade para exploração
    return score + random.randint(-5, 5)

# Preferência: se sou investidor, prioriza startups; se sou startup, prioriza investidores
candidates = [p for p in profiles if (my_type=="investor" and p.get("type")=="startup") or (my_type=="startup" and p.get("type")=="investor")]
candidates = sorted(candidates, key=rec_score, reverse=True)

st.session_state.setdefault("rec_idx", 0)
idx = st.session_state["rec_idx"] % max(1, len(candidates))
view = candidates[idx:idx+3]  # “carrossel” de 3 cards

col_nav1, col_nav2, col_nav3 = st.columns([1,6,1])
with col_nav1:
    if st.button("⬅️"):
        st.session_state["rec_idx"] = (st.session_state["rec_idx"] - 3) % max(1, len(candidates))
        st.rerun()
with col_nav3:
    if st.button("➡️"):
        st.session_state["rec_idx"] = (st.session_state["rec_idx"] + 3) % max(1, len(candidates))
        st.rerun()

st.caption("Dica: as recomendações combinam similaridade (tags/estágio/ticket) com um pouco de exploração para descobrir oportunidades não óbvias.")

cols = st.columns(3)
for c, p in zip(cols, view):
    with c:
        score, breakdown, dist = compat_breakdown(p, st.session_state)
        st.markdown(f"### {icon_of(p)} {p.get('name','')}")
        st.caption(f"{p.get('headline','')} • {p.get('city','')} • ~{dist} km")
        st.progress(score, text=f"Compatibilidade: {score}%")
        # por quê este match?
        st.markdown("**Por que sugerimos:**")
        reasons = []
        if breakdown["Tags"] >= 70: reasons.append("tags muito alinhadas")
        elif breakdown["Tags"] >= 40: reasons.append("algumas tags em comum")
        if breakdown["Estágio"] >= 80: reasons.append("estágio compatível")
        if breakdown["Ticket"] >= 70: reasons.append("rodada dentro do seu ticket")
        if breakdown["Distância"] >= 80: reasons.append("perto de você")
        if not reasons: reasons = ["boa complementaridade geral"]
        st.write(" • " + " | ".join(reasons))
        st.button("💙 Curtir (demo)", key=f"rec_like_{p.get('id',p.get('name','x'))}")
