import streamlit as st

st.title("🚀 Investor Match — Apresentação")

st.markdown("""
Bem-vindo! Esta é uma **demo clicável** do nosso app que conecta **startups e investidores**.  
A ideia é simples: **descoberta rápida** (estilo swipe), **conversa eficiente** e **fechamento de calls** — tudo no mesmo lugar.
""")

st.subheader("🥇 Proposta de Valor")
st.markdown("""
- **Para Startups:** menos tempo prospectando, mais reuniões com investidores **alinhados à tese**.  
- **Para Investidores:** dealflow **curado**, com **pitch de 1 minuto** e filtros avançados (setor, ticket, região).  
""")

st.subheader("✨ Diferenciais (além do Tinder)")
st.markdown("""
1. **Filtros por Tese e Localização (Pro)**  
2. **Compatibilidade por Tags** (% + barra visual)  
3. **Pitch em Vídeo** (1 min, opcional)  
4. **Agendar Call** direto pelo chat (Meet)  
5. **Clube Deal** (matches em grupo)  
6. **Quem curtiu você** (paywall Pro)  
7. **Status Online / Último Acesso e Mensagens Lidas** (Pro)  
8. **Feed de Updates** (para acompanhar teses e progresso)
""")

st.subheader("🧭 Como navegar na demo")
st.markdown("""
- **Explorar (Swipe)** → veja cards, compatibilidade e pitch.  
- **Mensagens** → após um match (use *Forçar Match* para acelerar), experimente o chat, **agendar call** e **clube deal**.  
- **Meu Perfil** → atualize **foto**, **localização** e veja **quem curtiu você** (paywall Pro).  
- **Assinatura Pro** → veja benefícios e ative (simulação).  
- **Admin (demo)** → painel com KPIs, filtros, exportação e relatórios.  
""")

st.subheader("🛣️ Roadmap sugerido")
st.markdown("""
- **MVP** (4–6 semanas): swipe, perfis, matches, chat básico, assinatura Pro inicial.  
- **Versão 1**: filtros por tese/localização, pitch em vídeo, agendar call.  
- **Versão 2**: clube deal, analytics, integrações (Calendly/Google Calendar/CRM), moderação e KYC.  
""")

st.subheader("💰 Monetização")
st.markdown("""
- **Assinatura Pro** (R$ 39,90/mês): filtros avançados, ver quem curtiu, status/leituras, super like/boost.  
- **Planos B2B** para funds/VCs com times (multiusuário) e **relatórios**.  
""")

st.info("Esta interface é apenas para demonstração. No app final, o menu lateral será substituído por navegação própria (tab bar).")
