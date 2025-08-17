# pages/03_Mensagens.py
import json
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def norm(p): return p.replace("\\","/") if isinstance(p,str) else p

@st.cache_data
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

st.set_page_config(page_title="Mensagens", page_icon="💬", layout="centered")
st.markdown("""
<style>
.app { max-width: 480px; margin: 0 auto; }
.msg { padding:10px 12px; border-radius:12px; margin:6px 0; max-width: 90%; }
.me  { background:#e8f0ff; margin-left:auto; }
.them{ background:#f5f5f5; margin-right:auto; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app">', unsafe_allow_html=True)
st.markdown("## 💬 Mensagens")

st.session_state.setdefault("matches", set())
st.session_state.setdefault("chat_with", None)
st.session_state.setdefault("chats", {})

profiles = load_profiles()
match_ids = list(st.session_state.get("matches") or [])
if not match_ids:
    st.info("Sem matches. Volte ao **Explorar (Swipe)** e curta alguns perfis.")
    st.markdown("</div>", unsafe_allow_html=True); st.stop()

if st.session_state["chat_with"] is None:
    last = st.session_state.get("last_match_idx")
    st.session_state["chat_with"] = last if last in match_ids else match_ids[-1]

pid = st.session_state["chat_with"]
other = next((x for x in profiles if x.get("id")==pid), None)
if not other:
    st.warning("Não foi possível carregar o match."); st.markdown("</div>", unsafe_allow_html=True); st.stop()

with st.container(border=True):
    c1, c2 = st.columns([1,4])
    with c1:
        img_rel = norm(other.get("image",""))
        if img_rel and not img_rel.startswith("http") and (BASE_DIR / img_rel).exists():
            st.image(img_rel, width=90)
        elif img_rel.startswith("http"):
            st.image(img_rel, width=90)
        else:
            st.image("https://via.placeholder.com/180.png?text=Perfil", width=90)
    with c2:
        st.markdown(f"**Chat com {other.get('name','')} — {other.get('headline','')}**")
        st.caption(other.get("bio",""))

hist = st.session_state["chats"].setdefault(pid, [])

st.markdown("---")
for who, text in hist:
    klass = "me" if who=="me" else "them"
    st.markdown(f'<div class="msg {klass}">{text}</div>', unsafe_allow_html=True)

st.markdown("---")
with st.form(key=f"form_{pid}", clear_on_submit=True):
    msg = st.text_input("Sua mensagem", key=f"msg_{pid}")
    ok = st.form_submit_button("Enviar", use_container_width=True)
    if ok and msg.strip():
        hist.append(("me", msg.strip()))
        hist.append(("them", "Perfeito! Vamos marcar uma call? 😊"))
        st.session_state["chats"][pid] = hist
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
