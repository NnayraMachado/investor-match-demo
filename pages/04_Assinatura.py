import streamlit as st

st.set_page_config(page_title="Assinatura", page_icon="⭐", layout="centered")
st.title("⭐ Assinatura Pro")

beneficios_free = [
    "Swipe básico com limite de likes/hora",
    "Chat e convite .ics",
    "Pitch em vídeo (até 1 min)",
]

beneficios_pro = [
    "Compatibilidade Avançada + Radar (Tags, Estágio, Ticket, Distância)",
    "Métricas no card de startups (MRR, Growth, Churn)",
    "Dealroom privado (arquivos, tarefas, checklist, integrações demo)",
    "Recomendações inteligentes (matches não óbvios)",
    "Eventos/Demo Day exclusivos",
    "Filtros e exportações em Tendências / Ranking",
    "Rewind (desfazer) e Boost semanal",
    "Ver quem curtiu você (acesso completo)",
    "Badges de verificação avançada",
]

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Free")
    for b in beneficios_free:
        st.markdown(f"- {b}")
with col2:
    st.markdown("### Pro")
    for b in beneficios_pro:
        st.markdown(f"- **{b}**")

st.markdown("---")
st.subheader("Planos (demo)")
colA, colB = st.columns(2)
with colA:
    st.markdown("**Mensal**")
    st.markdown("**R$ 39,90/mês**")
    if st.button("Ativar Pro Mensal (simulação)"):
        st.session_state["user_plan"] = "Pro"
        st.session_state["boost_left"] = 1
        st.balloons()
        st.success("Plano Pro (Mensal) ativado! Explore o Swipe e o Dealroom.")
with colB:
    st.markdown("**Anual**")
    st.markdown("**R$ 399/ano** (2 meses grátis)")
    if st.button("Ativar Pro Anual (simulação)"):
        st.session_state["user_plan"] = "Pro"
        st.session_state["boost_left"] = 2
        st.balloons()
        st.success("Plano Pro (Anual) ativado! Você ganhou 2 Boosts iniciais.")

st.info("Simulação para demo — sem cobrança real.")
