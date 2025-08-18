import streamlit as st
import random, json
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Tendências", page_icon="📈", layout="centered")
st.title("📈 Tendências do Ecossistema")

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

@st.cache_data
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

profiles = load_profiles()
st.session_state.setdefault("user_plan", st.session_state.get("user_plan","Free"))

# ---- simulação de série (12 semanas) e scores por setor ----
@st.cache_data
def trend_last_3m(seed:int=123):
    random.seed(seed)
    base = 100
    series = []
    for _ in range(12):  # 12 semanas
        base += random.randint(-3, 6)
        series.append(max(80, base))
    delta = series[-1] - series[0]
    label = "🔼 Otimista" if delta > 5 else ("➖ Moderado" if -5 <= delta <= 5 else "🔽 Cauteloso")
    sectors = {
        "SaaS": random.randint(60, 95),
        "Fintech": random.randint(60, 95),
        "Health": random.randint(45, 85),
        "Agtech": random.randint(40, 80),
        "AI": random.randint(65, 98),
        "Cripto": random.randint(30, 90),
        "Clima": random.randint(50, 88),
        "Educação": random.randint(40, 82),
        "Logística": random.randint(45, 86),
        "Marketplace": random.randint(45, 88),
    }
    return series, delta, label, sectors

series, delta, label, sectors = trend_last_3m()

colA, colB = st.columns([1,1])
with colA:
    st.subheader("Índice de apetite (últ. 3m)")
    st.caption(f"Sinal atual: **{label}**  |  Variação: **{('+' if delta>0 else '')}{delta} pts**")
    st.line_chart(series, height=180)
with colB:
    st.subheader("Setores em destaque")
    top = sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:5]
    st.write("\n".join([f"• **{k}** — score {v}" for k,v in top]))

st.divider()

# ---- Pro: filtros e exportação ----
if st.session_state.get("user_plan") == "Pro":
    st.subheader("🎯 Filtros (Pro)")
    all_tags = sorted({t for p in profiles for t in p.get("tags",[])})
    colf1, colf2, colf3 = st.columns(3)
    with colf1: tags_sel = st.multiselect("Setores", all_tags[:20], [])
    with colf2: stages_sel = st.multiselect("Estágio", ["Pre-Seed","Seed","Series A"], [])
    with colf3: regions_sel = st.multiselect("Região", sorted({p.get("country","") for p in profiles if p.get("country")}), [])
    st.caption("Os filtros são ilustrativos; dados são simulados.")

# ---- Dealflow Heat (simulado) ----
st.subheader("🔥 Dealflow Heat por estágio (volume relativo)")
random.seed(77)
heat = pd.DataFrame({
    "Estágio": ["Pre-Seed","Seed","Series A"],
    "Volume Relativo": [random.randint(40, 80), random.randint(60, 100), random.randint(30, 70)]
}).set_index("Estágio")
st.bar_chart(heat)

# ---- Ranking de startups por crescimento (usa metrics se houver) ----
st.subheader("🚀 Startups com melhor growth (últimos meses)")
rows = []
for p in profiles:
    if p.get("type") == "startup" and isinstance(p.get("metrics"), dict):
        growth = int(100 * p["metrics"].get("growth_rate", 0))
        churn = int(100 * p["metrics"].get("churn", 0))
        rows.append({
            "Icon": p.get("icon","🚀"),
            "Startup": p.get("name",""),
            "Setores": ", ".join(p.get("tags",[])),
            "Growth (%)": growth,
            "Churn (%)": churn,
            "MRR (USD)": p["metrics"].get("MRR", 0)
        })

if rows:
    df_growth = pd.DataFrame(rows).sort_values(["Growth (%)","MRR (USD)"], ascending=False)
    st.dataframe(df_growth, hide_index=True, use_container_width=True)
    if st.session_state.get("user_plan") == "Pro":
        csv = df_growth.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar CSV", csv, "ranking_growth.csv", "text/csv")
else:
    st.info("Ainda não há startups com métricas registradas no profiles.json (campo `metrics`).")

st.divider()

# ---- Seção Pro: análise completa ----
if st.session_state.get("user_plan") != "Pro":
    st.warning("🔒 No **Pro** você vê análise por **setor**, **região**, **volatilidade** e recomendações acionáveis.")
else:
    st.subheader("Análise completa (Pro)")
    # pontuação por setor
    st.markdown("**Pontuação por setor** (quanto maior, mais 'quente'):")
    st.bar_chart({k:v for k,v in sectors.items()})
    # volatilidade (simulada)
    st.markdown("**Volatilidade** (baixa é melhor para previsibilidade):")
    vol = {k: max(5, int((100 - v)/3) + random.randint(0,6)) for k,v in sectors.items()}
    st.bar_chart(vol)
    # recomendações
    st.markdown("**Recomendações**")
    hot = [k for k,v in sectors.items() if v >= 80]
    warm = [k for k,v in sectors.items() if 65 <= v < 80]
    cool = [k for k,v in sectors.items() if v < 65]
    bullets = []
    if hot: bullets.append(f"Priorize **{', '.join(hot)}** — apetite elevado.")
    if warm: bullets.append(f"Mantenha radar em **{', '.join(warm)}** — apetite moderado.")
    if cool: bullets.append(f"Evite foco agora em **{', '.join(cool[:4])}** — apetite baixo/volatilidade alta.")
    for b in bullets: st.write("• " + b)
    st.info("Observação: dados de tendências são **simulados para demo**. Em produção, integraríamos fontes e telemetria real.")
