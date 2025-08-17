# pages/03_Mensagens.py
import json, time, uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
import streamlit as st

# ---------- paths / helpers ----------
BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def norm(p): return p.replace("\\","/") if isinstance(p,str) else p

@st.cache_data
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def human_last_seen(is_online: bool, last_seen_min: int|None) -> str:
    if is_online: return "🟢 online agora"
    if last_seen_min is None: return "visto recentemente"
    if last_seen_min < 60: return f"visto há {last_seen_min} min"
    h = last_seen_min // 60
    return f"visto há {h} h"

def avatar(img_rel: str|None, width: int = 88):
    img_rel = norm(img_rel or "")
    if img_rel and not img_rel.startswith("http") and (BASE_DIR / img_rel).exists():
        st.image(img_rel, width=width)
    elif img_rel.startswith("http"):
        st.image(img_rel, width=width)
    else:
        st.image("https://via.placeholder.com/176.png?text=Perfil", width=width)

# ---------- state ----------
st.session_state.setdefault("matches", set())
st.session_state.setdefault("chat_with", None)
st.session_state.setdefault("chats", {})          # {profile_id: [ {sender,text,ts,delivered_at,read_at,id} ]}
st.session_state.setdefault("typing_their_until", 0.0)  # timestamp
st.session_state.setdefault("user_name", "Você")

# ---------- page ----------
st.set_page_config(page_title="Mensagens", page_icon="💬", layout="centered")

# CSS compacto, recibos e bolha "digitando..."
st.markdown("""
<style>
.app { max-width: 480px; margin: 0 auto; }
.header-line { display:flex; gap:16px; align-items:center; }
.badge { display:inline-block; font-size:12px; padding:3px 8px; border-radius:8px; border:1px solid #e5e7eb; background:#f8fafc; margin-right:6px; }
.msg-wrap { margin-top:10px; }
.msg { padding:10px 12px; border-radius:12px; margin:6px 0; max-width: 90%; }
.me  { background:#e8f0ff; margin-left:auto; }
.them{ background:#f5f5f5; margin-right:auto; }
.meta { color:#6b7280; font-size:12px; margin-top:2px; text-align:right; }
.typing { font-size:12px; color:#6b7280; margin:4px 0 8px; }
.section { margin-top:16px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app">', unsafe_allow_html=True)
st.markdown("## 💬 Mensagens")

profiles = load_profiles()

# --- matches / seleção ---
match_ids = list(st.session_state.get("matches") or [])
if not match_ids:
    st.info("Você ainda não tem matches. Volte ao **Explorar (Swipe)** e curta alguns perfis.")
    st.markdown("</div>", unsafe_allow_html=True); st.stop()

if st.session_state["chat_with"] is None:
    last = st.session_state.get("last_match_idx")
    st.session_state["chat_with"] = last if last in match_ids else match_ids[-1]

pid = st.session_state["chat_with"]
other = next((x for x in profiles if x.get("id")==pid), None)
if not other:
    st.warning("Não foi possível carregar o match selecionado.")
    st.markdown("</div>", unsafe_allow_html=True); st.stop()

# --- header do chat (foto, verificado, online/último acesso) ---
with st.container(border=True):
    c1, c2 = st.columns([1,4])
    with c1:
        avatar(other.get("image",""), width=88)
    with c2:
        verified = other.get("verified", True)  # fallback demo: quase todos verificados
        headline = other.get("headline","")
        is_online = other.get("is_online", True)
        last_seen_min = other.get("last_seen_min", 5)
        st.markdown(
            f"<div class='header-line'>"
            f"<div><b>Chat com {other.get('name','')}</b>"
            f"{' <span class=\"badge\">🛡️ Verificado</span>' if verified else ''}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        st.caption(f"{headline} • {human_last_seen(is_online,last_seen_min)}")
        if other.get("bio"):
            st.caption(other["bio"])

# --- ALERTA DE SEGURANÇA (demo) ---
with st.expander("🔒 Dicas rápidas de segurança"):
    st.markdown(
        "- Nunca envie chaves privadas, código de autenticação ou dados bancários pelo chat.\n"
        "- Desconfie de pedidos de adiantamento fora da plataforma.\n"
        "- Prefira **calls gravadas** e **documentos assinados**.\n"
        "- Perfis **Verificados** passam checagens de identidade/documentos."
    )

# --- histórico ---
now = time.time()
hist = st.session_state["chats"].setdefault(pid, [])  # list de dicts

st.markdown("----")
st.caption("Histórico")
st.markdown("<div class='msg-wrap'>", unsafe_allow_html=True)

for m in hist:
    who = m["sender"]
    klass = "me" if who=="me" else "them"
    st.markdown(f"<div class='msg {klass}'>{m['text']}</div>", unsafe_allow_html=True)

    # recibos de entrega/leitura (apenas para minhas mensagens)
    if who == "me":
        delivered = now >= m.get("delivered_at", 0)
        read = now >= m.get("read_at", 0)
        if read:
            st.markdown("<div class='meta'>✔✔ lido</div>", unsafe_allow_html=True)
        elif delivered:
            st.markdown("<div class='meta'>✔ entregue</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# --- indicador de "digitando..." do outro lado (simulado quando você digita) ---
if now < st.session_state["typing_their_until"]:
    st.markdown("<div class='typing'>✍️ digitando…</div>", unsafe_allow_html=True)

st.markdown("----")

# --- envio de mensagens ---
with st.form(key=f"form_send_{pid}", clear_on_submit=True):
    msg = st.text_input("Sua mensagem", key=f"msg_input_{pid}",
                        on_change=lambda: st.session_state.update(typing_their_until=time.time()+2))
    sent = st.form_submit_button("Enviar", use_container_width=True)
    if sent and msg.strip():
        ts = time.time()
        # minha msg com metas de entrega/leitura (simuladas)
        hist.append({
            "id": str(uuid.uuid4()),
            "sender": "me",
            "text": msg.strip(),
            "ts": ts,
            "delivered_at": ts + 0.8,   # ~800ms
            "read_at": ts + 2.2         # ~2.2s
        })
        # resposta automática de demonstração
        hist.append({
            "id": str(uuid.uuid4()),
            "sender": "them",
            "text": "Perfeito! Vamos marcar uma call? 😊",
            "ts": ts + 1.0
        })
        st.session_state["chats"][pid] = hist
        st.rerun()

# --- agenda / call (demo) ---
st.markdown("----")
st.subheader("📅 Agendar call (demo)")

# sugestões rápidas (próximos dias/horas)
opts = []
base = datetime.now()
for d in (1, 2, 3):   # amanhã, +2, +3 dias
    for hr in (10, 14, 18):
        t = (base + timedelta(days=d)).replace(hour=hr, minute=0, second=0, microsecond=0)
        opts.append(t)

chosen = st.selectbox(
    "Sugestão de horário",
    options=[o.strftime("%d/%m %H:%M") for o in opts],
    index=0
)
title = st.text_input("Título da call", value=f"Call: {st.session_state.get('user_name','Você')} × {other.get('name','')}")
meet_link = st.text_input("Link de vídeo (demo)", value="https://meet.google.com/xxx-xxxx-xxx")

# gera ICS para baixar
def make_ics(summary: str, start_dt: datetime, duration_min: int = 30, url: str = "") -> str:
    dtstart = start_dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dtend = (start_dt + timedelta(minutes=duration_min)).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    uid = f"{uuid.uuid4()}@investor-match"
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Investor Match Demo//PT-BR",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:Convite gerado no Investor Match Demo\\n{url}",
        f"URL:{url}",
        "END:VEVENT",
        "END:VCALENDAR"
    ]
    return "\r\n".join(lines)

colA, colB = st.columns(2)
with colA:
    if st.button("📨 Gerar convite (.ics)", use_container_width=True, key="make_ics"):
        pick = opts[[o.strftime("%d/%m %H:%M") for o in opts].index(chosen)]
        ics_content = make_ics(title, pick, 30, meet_link)
        st.download_button("⬇️ Baixar .ics", ics_content, file_name="convite_call.ics", mime="text/calendar", use_container_width=True)
with colB:
    st.link_button("▶️ Abrir link de vídeo (demo)", meet_link, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)
