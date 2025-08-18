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
        return data
    return []

def icon_of(p): return p.get("icon","💰" if p.get("type")=="investor" else "🚀")

st.set_page_config(page_title="Recomendações", page_icon="✨", layout="centered")
st.title("✨ Recomendações inteligentes")

if st.session_state.get("user_plan")!="Pro":
    st.warning("🔒 As recomendações avançadas fazem parte do **Pro**.")
    st.stop()

profiles = load_profiles()
my_tags = set(t.lower() for t in st.session_state.get("my_tags",[]))
my_stage = st.session_state.get("my_stage","Seed")
my_type = st.session_state.get("my_type","investor")

def score(p):
    # Heurística: combina similaridade de tags + diversidade controlada (exploration)
    tags = set(t.lower() for t in p.get("tags",[]))
    overlap = len(my_tags & tags) / max(1,len(my_tags | tags))
    same_stage = 1.0 if p.get("stage")==my_stage else 0.6
    diversity = 0.3 if len(tags - my_tags) >= 2 else 0.0
    # se sou investidor, prioriza startups; se sou startup, prioriza investidores
    type_bonus = 1.0 if (my_type=="investor" and p.get("type")=="startup") or (my_type=="startup" and p.get("type")=="investor") else 0.7
    sc = 0.6*overlap + 0.2*same_stage + 0.2*(diversity) 
    return sc*type_bonus

candid = sorted(profiles, key=lambda p: score(p), reverse=True)[:8]
for p in candid:
    with st.container(border=True):
        st.markdown(f"**{icon_of(p)} {p['name']}**")
        st.caption(f"{p.get('headline','')} • estágio {p.get('stage','Seed')}")
        st.write(", ".join(p.get("tags",[])))
        st.button("💙 Curtir (demo)", key=f"ai_like_{p.get('id',p['name'])}")
