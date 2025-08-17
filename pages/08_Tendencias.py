import streamlit as st
import random

st.title("📈 Tendências do Ecossistema (demo)")

@st.cache_data
def trend_last_3m(seed:int=123):
    random.seed(seed)
    base = 100
    series = []
    for _ in range(12):  # 12 semanas ~ 3 meses
        base += random.randint(-3, 6)
        series.append(max(80, base))
    delta = series[-1] - series[0]
    label = "🔼 Otimista" if delta > 5 else ("➖ Moderado" if -5 <= delta <= 5 else "🔽 Cauteloso")
    # setores com “pontuação” fictícia
    sectors = {
        "SaaS": random.randint(60, 95),
        "Fintech": random.randint(60, 95),
        "Health": random.randint(45, 85),
        "Agtech": random.randint(40, 80),
        "AI": random.randint(65, 98),
        "Cripto": random.randint(30, 90),
        "Clima": random.randint(50, 88),
        "Educação": random.randint(40, 82),
    }
    return series, delta, label, sectors

series, delta, label, sectors = trend_last_3m()

colA, colB = st.columns([1,1])
with colA:
    st.subheader("Índice de apetite (últ. 3m)")
    st.caption(f"Sinal atual: **{label}**  |  Variação: **{('+' if delta>0 else '')}{delta} pts**")
    st.line_chart(series, height=160)
with colB:
    st.subheader("Setores em destaque")
    top = sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:5]
    st.write("\n".join([f"• **{k}** — score {v}" for k,v in top]))

st.divider()

if st.session_state.get("user_plan") != "Pro":
    st.warning("🔒 Este é um **preview**. No Pro você vê a análise completa por **setor**, **região**, **volatilidade** e **recomendações**.")
else:
    st.subheader("Análise completa (Pro)")
    # Quebra por setor (gráfico)
    st.markdown("**Pontuação por setor** (quanto maior, mais 'quente'):")
    st.bar_chart({k:v for k,v in sectors.items()})
    # Volatilidade fictícia
    st.markdown("**Volatilidade** (baixa é melhor para previsibilidade):")
    vol = {k: max(5, int((100 - v)/3) + random.randint(0,6)) for k,v in sectors.items()}
    st.bar_chart(vol)
    # Recomendações
    st.markdown("**Recomendações**")
    bullets = []
    hot = [k for k,v in sectors.items() if v >= 80]
    warm = [k for k,v in sectors.items() if 65 <= v < 80]
    cool = [k for k,v in sectors.items() if v < 65]
    if hot: bullets.append(f"Priorize **{', '.join(hot)}** — apetite elevado.")
    if warm: bullets.append(f"Mantenha radar em **{', '.join(warm)}** — apetite moderado.")
    if cool: bullets.append(f"Evite alocar esforço agora em **{', '.join(cool[:3])}** — apetite baixo/volatilidade alta.")
    for b in bullets: st.write("• " + b)
    st.info("Observação: dados de tendências são **simulados para demo**. No produto, integramos fontes e telemetria real.")
