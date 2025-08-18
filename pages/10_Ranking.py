import streamlit as st
import pandas as pd
import random, json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

@st.cache_data
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def icon_of(p): return p.get("icon","💰" if p.get("type")=="investor" else "🚀")

st.set_page_config(page_title="Ranking", page_icon="🏆", layout="centered")
st.title("🏆 Ranking & Destaques")

profiles = load_profiles()
if not profiles: st.info("Sem dados."); st.stop()

random.seed(42)
tops = []
for p in profiles:
    tops.append({
        "icon": icon_of(p),
        "Nome": p["name"],
        "Curtidas (semana)": random.randint(5, 80),
        "Matches (semana)": random.randint(1, 20),
        "Taxa de resposta (%)": random.randint(50, 98)
    })
df = pd.DataFrame(tops).sort_values("Matches (semana)", ascending=False).reset_index(drop=True)

st.dataframe(df, hide_index=True, use_container_width=True)
st.markdown("---")
if st.session_state.get("user_plan")!="Pro":
    st.warning("🔒 No Pro você destrava filtros por **setor**, **estágio**, **região** e exportação CSV.")
else:
    colA,colB,colC = st.columns(3)
    with colA:
        sector = st.multiselect("Filtrar setor", sorted({t for p in profiles for t in p.get("tags",[])})[:12])
    with colB:
        stg = st.multiselect("Estágio", ["Pre-Seed","Seed","Series A"])
    with colC:
        reg = st.multiselect("Região", sorted({p.get("country","") for p in profiles if p.get("country")}), [])
    st.info("Filtros ilustrativos (demo).")
