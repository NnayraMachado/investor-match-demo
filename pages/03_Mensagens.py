# pages/03_Mensagens.py
import json, time, uuid, math, random
from datetime import datetime as _dt, timedelta, timezone
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for p in data:
            p.setdefault("type","investor")
            p.setdefault("icon","💰" if p["type"]=="investor" else "🚀")
            p.setdefault("lat", None); p.setdefault("lon", None)
        return data
    return []

def profile_icon(p): return p.get("icon") or ("💰" if p.get("type")=="investor" else "🚀")

def human_last_seen(is_online: bool, last_seen_min: int|None) -> str:
    if is_online: return "🟢 online agora"
    if last_seen_min is None: return "visto recentemente"
    if last_seen_min < 60: return f"visto há {last_seen_min} min"
    h = last_seen_min // 60
    return f"visto há {h} h"

# distância
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def distance_label(other_profile: dict) -> str:
    my_lat = st.session_state.get("my_lat")
    my_lon = st.session_state.get("my_lon")
    lat2 = other_profile.get("lat"); lon2 = other_profile.get("lon")
    if all(v is not None for v in (my_lat, my_lon, lat2, lon2)):
        km = haversine_km(my_lat, my_lon, lat2, lon2)
        return f"~{int(round(km))} km de você"
    rnd = random.Random(other_profile.get("id",0)); return f"~{rnd.randint(1,25)} km de você"

# ---------- state ----------
st.session_state.setdefault("matches", set())
st.session_state.setdefault("chat_with", None)
st.session_state.setdefault("chats", {})
st.session_state.setdefault("typing_their_until", 0.0)
st.session_state.setdefault("user_name", "Você")
st.session_state.setdefault("my_lat", -23.5505)
st.session_state.setdefault("my_lon", -46.6333)

st.set_page_config(page_title="Mensagens", page_icon="💬", layout="centered")

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
.icon-avatar { width: 88px; height: 88px; border-radius: 50%;
               background:#eef2f7; display:flex; align-items:center; justify-content:center; }
.icon-avatar span { font-size: 44px; }
.distance { color:#6b7280; font-size:12px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app">', unsafe_allow_html=True)
st.markdown("## 💬 Mensagens")

profiles = load_profiles()
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

with st.container(border=True):
    c1, c2 = st.columns([1,4])
    with c1:
        st.markdown(f'<div class="icon-avatar"><span>{profile_icon(other)}</span></div>', unsafe_allow_html=True)
    with c2:
        verified = other.get("verified", True)
        headline = other.get("headline","")
        is_online = other.get("is_online", True)
        last_seen_min = other.get("last_seen_min", 5)
        st.markdown(
            f"<div class='header-line'>"
            f"<div><b>{profile_icon(other)} Chat com {other.get('name','')}</b>"
            f"{' <span class=\"badge\">🛡️ Verificado</span>' if verified else ''}</div>"
            f"</div>", unsafe_allow_html=True
        )
        st.caption(f"{headline} • {human_last_seen(is_online,last_seen_min)}")
        st.markdown(f"<span class='distance'>{distance_label(other)}</span>", unsafe_allow_html=True)
        if other.get("bio"): st.caption(other["bio"])

with st.expander("🔒 Dicas rápidas de segurança"):
    st.markdown("- Nunca envie chaves privadas, códigos ou dados bancários.\n- Prefira **calls gravadas** e **documentos assinados**.\n- Perfis **Verificados** passam checagens de identidade.")

now = time.time()
hist = st.session_state["chats"].setdefault(pid, [])

st.markdown("----")
st.caption("Histórico")
st.markdown("<div class='msg-wrap'>", unsafe_allow_html=True)
for m in hist:
    who = m["sender"]; klass = "me" if who=="me" else "them"
    st.markdown(f"<div class='msg {klass}'>{m['text']}</div>", unsafe_allow_html=True)
    if who == "me":
        delivered = now >= m.get("delivered_at", 0); read = now >= m.get("read_at", 0)
        if read: st.markdown("<div class='meta'>✔✔ lido</div>", unsafe_allow_html=True)
        elif delivered: st.markdown("<div class='meta'>✔ entregue</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

if now < st.session_state["typing_their_until"]:
    st.markdown("<div class='typing'>✍️ digitando…</div>", unsafe_allow_html=True)

st.markdown("----")

input_key = f"msg_input_{pid}"; last_key  = f"__last_val_{pid}"
with st.form(key=f"form_send_{pid}", clear_on_submit=True):
    msg = st.text_input("Sua mensagem", key=input_key)
    sent = st.form_submit_button("Enviar", use_container_width=True)

cur_val = st.session_state.get(input_key, ""); prev_val = st.session_state.get(last_key, "")
if cur_val != prev_val: st.session_state["typing_their_until"] = time.time() + 2
st.session_state[last_key] = cur_val

if sent and msg.strip():
    ts = time.time()
    hist.append({"id": str(uuid.uuid4()), "sender": "me","text": msg.strip(),"ts": ts,"delivered_at": ts + 0.8,"read_at": ts + 2.2})
    hist.append({"id": str(uuid.uuid4()), "sender": "them","text": "Perfeito! Vamos marcar uma call? 😊","ts": ts + 1.0})
    st.session_state["chats"][pid] = hist
    st.rerun()

st.markdown("----")
st.subheader("📅 Agendar call (demo)")
opts = []; base = _dt.now()
for d in (1, 2, 3):
    for hr in (10, 14, 18):
        t = (base + timedelta(days=d)).replace(hour=hr, minute=0, second=0, microsecond=0)
        opts.append(t)

chosen = st.selectbox("Sugestão de horário", options=[o.strftime("%d/%m %H:%M") for o in opts], index=0)
title = st.text_input("Título da call", value=f"Call: {st.session_state.get('user_name','Você')} × {other.get('name','')}")
meet_link = st.text_input("Link de vídeo (demo)", value="https://meet.google.com/xxx-xxxx-xxx")

def make_ics(summary: str, start_dt: _dt, duration_min: int = 30, url: str = "") -> str:
    dtstart = start_dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dtend = (start_dt + timedelta(minutes=duration_min)).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    import uuid
    uid = f"{uuid.uuid4()}@investor-match"
    lines = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Investor Match Demo//PT-BR","BEGIN:VEVENT",
             f"UID:{uid}",f"DTSTAMP:{_dt.utcnow().strftime('%Y%m%dT%H%M%SZ')}",f"DTSTART:{dtstart}",f"DTEND:{dtend}",
             f"SUMMARY:{summary}",f"DESCRIPTION:Convite gerado no Investor Match Demo\\n{url}",f"URL:{url}","END:VEVENT","END:VCALENDAR"]
    return "\r\n".join(lines)

colA, colB, colC = st.columns(3)
with colA:
    if st.button("📨 Gerar convite (.ics)", use_container_width=True, key="make_ics"):
        pick = opts[[o.strftime("%d/%m %H:%M") for o in opts].index(chosen)]
        ics_content = make_ics(title, pick, 30, meet_link)
        st.download_button("⬇️ Baixar .ics", ics_content, file_name="convite_call.ics", mime="text/calendar", use_container_width=True)
with colB:
    st.link_button("▶️ Abrir link de vídeo", meet_link, use_container_width=True)
with colC:
    if st.button("📂 Abrir Dealroom", use_container_width=True):
        st.switch_page("pages/09_Dealroom.py")

st.markdown("</div>", unsafe_allow_html=True)
