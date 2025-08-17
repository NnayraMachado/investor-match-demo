# pages/03_Mensagens.py
import json, time, random
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILES_JSON = BASE_DIR/"assets"/"profiles.json"

@st.cache_data
def load_profiles():
    with open(PROFILES_JSON,"r",encoding="utf-8") as f: 
        return json.load(f)

profiles = load_profiles()
matches = list(st.session_state.get("matches", set()))

# CSS balões de chat
st.markdown("""
<style>
.msg {padding:8px 12px; border-radius:14px; margin:6px 0; max-width:78%;}
.me  {background:#e9f5ff; margin-left:auto;}
.them{background:#f5f5f5;}
.meta{font-size:11px; color:#777; margin-top:-4px;}
</style>
""", unsafe_allow_html=True)

_, mid, _ = st.columns([1,2,1])
with mid:
    st.markdown("### 💬 Mensagens")

    if not matches:
        st.write("Ainda não há *matches*. Volte ao **Explorar** e curta alguns perfis.")
        st.stop()

    for idx in matches:
        p = profiles[idx % len(profiles)]
        with st.expander(f"{p['name']} — {p['headline']}"):
            with st.container(border=True):
                # status (Pro)
                if st.session_state.get("user_plan") == "Pro":
                    status = "🟢 Online agora" if p.get("is_online") else f"⏱️ Último acesso há {p.get('last_seen_min', 15)} min"
                    st.caption(status)

                st.image(p["image"], width=100)
                st.write(p["bio"])

                key_history = f"chat_history_{idx}"
                if key_history not in st.session_state:
                    st.session_state[key_history] = []   # lista de tuplas: (autor, texto, status)

                # respostas rápidas
                st.caption("Respostas rápidas:")
                q1, q2, q3 = st.columns(3)
                with q1:
                    if st.button("👉 Enviar deck", key=f"qr1_{idx}"):
                        st.session_state[key_history].append(("Você","Segue meu deck. Podemos falar amanhã?","sent"))
                        st.rerun()
                with q2:
                    if st.button("📅 Marcar call", key=f"qr2_{idx}"):
                        st.session_state[key_history].append(("Você","Tem agenda na quinta às 15h?","sent"))
                        st.rerun()
                with q3:
                    if st.button("💬 Sobre a tese", key=f"qr3_{idx}"):
                        st.session_state[key_history].append(("Você","Nossa tese é SaaS B2B com LTV/CAC > 3.","sent"))
                        st.rerun()

                # input de mensagem
                msg = st.text_input("Sua mensagem", key=f"input_{idx}", placeholder="Digite e pressione Enter")
                if msg and ("Você", msg, "sent") not in st.session_state[key_history]:
                    # adiciona e simula status
                    st.session_state[key_history].append(("Você", msg, "delivered"))
                    if st.session_state.get("user_plan") == "Pro":
                        st.session_state[key_history][-1] = ("Você", msg, "read")

                    # resposta automática
                    with st.spinner("Digitando..."):
                        time.sleep(0.6)
                    st.session_state[key_history].append((p["name"], "Legal! Vamos marcar uma call para falar do deal?", "delivered"))
                    st.rerun()

                # render do histórico
                for autor, texto, status in st.session_state[key_history]:
                    align = "me" if autor == "Você" else "them"
                    st.markdown(f'<div class="msg {align}"><b>{autor}:</b> {texto}</div>', unsafe_allow_html=True)
                    if autor == "Você" and st.session_state.get("user_plan") == "Pro":
                        ticks = "✔✔" if status == "read" else "✔"
                        st.markdown(f'<div class="meta" style="text-align:right;">{ticks}</div>', unsafe_allow_html=True)

                st.divider()
                # Agendar call (demo)
                st.markdown("**Agendar Call (demo)**")
                slot = st.radio("Escolha um horário", ["Amanhã 10:00", "Amanhã 15:00", "Sexta 11:30"],
                                horizontal=True, key=f"slot_{idx}")
                if st.button("Gerar link de Meet (demo)", key=f"meet_{idx}"):
                    fake = f"https://meet.google.com/{random.choice(['abc-defg-hij','xyz-1234-pqr','invest-777'])}"
                    st.success(f"✅ Call confirmada: **{slot}** — Link: {fake}")

                st.divider()
                # Clube Deal (demo)
                st.markdown("**Clube Deal (demo)**")
                key_club = f"club_{idx}"
                if st.button("Criar Clube Deal", key=f"btn_club_{idx}"):
                    st.session_state[key_club] = random.randint(2, 6)
                if key_club in st.session_state:
                    n = st.session_state[key_club]
                    st.info(f"👥 Clube Deal criado com **{n} investidores** interessados.")
                    st.caption("No produto, aqui rolaria um chat em grupo e cap table compartilhada.")
