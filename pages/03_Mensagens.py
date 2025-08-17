# pages/03_Mensagens.py
import json
from pathlib import Path
import streamlit as st

# ---------- utils ----------
BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def norm_img_path(p):
    return p.replace("\\", "/") if isinstance(p, str) else p

@st.cache_data
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def show_thumb(img_rel: str, width: int = 110):
    img_rel = norm_img_path(img_rel or "")
    if img_rel and not img_rel.startswith("http") and (BASE_DIR / img_rel).exists():
        st.image(img_rel, width=width)
    elif img_rel.startswith("http"):
        st.image(img_rel, width=width)
    else:
        st.image("https://via.placeholder.com/220.png?text=Perfil", width=width)

# ---------- estado ----------
st.session_state.setdefault("matches", set())
st.session_state.setdefault("chat_with", None)
st.session_state.setdefault("chats", {})  # dict: id -> list[(sender, text)]

# ---------- page ----------
st.set_page_config(page_title="Mensagens", page_icon="💬", layout="centered")

# CSS compacto / tipo celular
st.markdown("""
<style>
.app-wrapper { max-width: 480px; margin: 0 auto; }
.msg-bubble { padding:10px 12px; border-radius:12px; margin:6px 0; max-width: 90%; }
.msg-me { background:#e8f0ff; margin-left:auto; }
.msg-them { background:#f5f5f5; margin-right:auto; }
.meta { color:#6b7280; font-size:12px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)
st.markdown("## 💬 Mensagens")

profiles = load_profiles()

# Lista de matches disponíveis (com fallback se não houver)
match_ids = list(st.session_state.get("matches") or [])
if not match_ids:
    st.info("Você ainda não tem matches. Volte ao **Explorar (Swipe)** e curta alguns perfis.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Se não tiver alguém selecionado, pegue o último match
if st.session_state["chat_with"] is None:
    last = st.session_state.get("last_match_idx")
    st.session_state["chat_with"] = last if last in match_ids else match_ids[-1]

# Perfil atual com quem estamos falando
pid = st.session_state["chat_with"]
other = next((x for x in profiles if x.get("id")==pid), None)

if not other:
    st.warning("Não foi possível carregar o match selecionado.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Cabeçalho do chat
with st.container(border=True):
    cL, cR = st.columns([1,4])
    with cL:
        show_thumb(other.get("image",""), width=110)
    with cR:
        st.markdown(f"**Chat com {other.get('name','')}** — {other.get('headline','')}")
        st.caption(other.get("bio",""))

# Área de histórico
hist = st.session_state["chats"].setdefault(pid, [])
st.markdown("---")
st.caption("Histórico")
for sender, text in hist:
    klass = "msg-me" if sender=="me" else "msg-them"
    align = "right" if sender=="me" else "left"
    st.markdown(f'<div class="msg-bubble {klass}" style="text-align:{align}">{text}</div>', unsafe_allow_html=True)

# Caixa de envio
st.markdown("---")
with st.form(key=f"form_send_{pid}", clear_on_submit=True):
    msg = st.text_input("Sua mensagem", key=f"msg_input_{pid}")
    sent = st.form_submit_button("Enviar", use_container_width=True)
    if sent and msg.strip():
        # grava minha msg
        hist.append(("me", msg.strip()))
        # resposta automática simples para demo
        reply = "Perfeito! Vamos marcar uma call? 😊"
        hist.append(("them", reply))
        st.session_state["chats"][pid] = hist
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
