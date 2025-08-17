import streamlit as st

st.title("⭐ Assinatura Pro")

beneficios = [
    "Filtros por tese e localização",
    "Rewind (desfazer último swipe)",
    "Super Like e Boost de visibilidade",
    "Ver quem curtiu você",
    "Status (online/último acesso) e leitura de mensagens",
    "Agendar call direto no chat",
]

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Free")
    st.markdown("- Swipes limitados\n- Sem filtros avançados\n- Sem ver quem curtiu\n- Chat sem status")
with col2:
    st.markdown("### Pro")
    for b in beneficios: st.markdown(f"- {b}")

st.markdown("---")
st.write("**Preço sugerido (demo):** R$ 39,90/mês ou R$ 399/ano.")

if st.button("Ativar Pro (simulação)"):
    st.session_state["user_plan"] = "Pro"
    st.balloons()
    st.success("Plano Pro ativado (simulação). Volte ao Explorar para usar recursos extras.")
