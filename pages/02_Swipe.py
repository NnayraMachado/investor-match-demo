# pages/02_Swipe.py
import json, math, random, time
from pathlib import Path
from secrets import randbelow
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"
FREE_LIKES_PER_HOUR = 10  # Free

def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for p in data:
            p.setdefault("pitch_url", None)
            p.setdefault("type", "investor")
            p.setdefault("icon", "💰" if p["type"] == "investor" else "🚀")
            p.setdefault("lat", None); p.setdefault("lon", None)
            p.setdefault("tags", p.get("tags", ["SaaS","Fintech"]))
            p.setdefault("stage", "Seed")
            p.setdefault("raising", 1500)        # mil USD
            p.setdefault("ticket_min", 100)
            p.setdefault("ticket_max", 2000)
        return data
    return []

def icon_of(p): return p.get("icon") or ("💰" if p.get("type")=="investor" else "🚀")

profiles = load_profiles()

# ---------- estado ----------
st.session_state.setdefault("swipe_idx", 0)
st.session_state.setdefault("matches", set())
st.session_state.setdefault("liked", set())
st.session_state.setdefault("passed", set())
st.session_state.setdefault("history", [])
st.session_state.setdefault("my_tags", ["SaaS", "Fintech"])
st.session_state.setdefault("user_plan", st.session_state.get("user_plan","Free"))
st.session_state.setdefault("my_lat", -23.5505)
st.session_state.setdefault("my_lon", -46.6333)
st.session_state.setdefault("boost_left", 1 if st.session_state["user_plan"]=="Pro" else 0)
st.session_state.setdefault("likes_used", st.session_state.get("likes_used",0))
st.session_state.setdefault("likes_reset_at", st.session_state.get("likes_reset_at", time.time()+3600))

def reset_like_window_if_needed():
    now = time.time()
    if now >= st.session_state["likes_reset_at"]:
        st.session_state["likes_reset_at"] = now + 3600
        st.session_state["likes_used"] = 0

def can_like():
    if st.session_state.get("user_plan")=="Pro":
        return True, None
    reset_like_window_if_needed()
    rem = max(0, FREE_LIKES_PER_HOUR - st.session_state["likes_used"])
    return rem > 0, rem

def they_like_back(profile_id: int) -> bool:
    key = f"likeback_{profile_id}"
    if key not in st.session_state:
        st.session_state[key] = randbelow(100) < 30
    return st.session_state[key]

# distância
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def distance_km(p):
    my_lat = st.session_state.get("my_lat"); my_lon = st.session_state.get("my_lon")
    lat2, lon2 = p.get("lat"), p.get("lon")
    if None not in (my_lat, my_lon, lat2, lon2):
        return int(round(haversine_km(my_lat, my_lon, lat2, lon2)))
    rnd = random.Random(p.get("id",0)); return rnd.randint(1,25)

# compatibilidade avançada (0–100)
def compat_score(p):
    my_tags = set(t.lower() for t in st.session_state.get("my_tags", []))
    their_tags = set(t.lower() for t in p.get("tags", []))
    jacc = (100 * len(my_tags & their_tags) / max(1, len(my_tags | their_tags)))

    # estágio e ticket (se eu for investidor)
    stage_fit = 100 if st.session_state.get("my_type","investor")=="investor" and st.session_state.get("my_stage") in [p.get("stage")] else (70 if st.session_state.get("my_type")=="startup" and p.get("stage")==st.session_state.get("my_stage","Seed") else 50)
    # ticket match
    raising = p.get("raising",1500)
    tmin = st.session_state.get("my_ticket_min", 100)
    tmax = st.session_state.get("my_ticket_max", 2000)
    if tmin <= raising <= tmax:
        ticket_fit = 100
    else:
        # penaliza proporcionalmente
        diff = min(abs(raising - max(tmin,tmax)), 2000)
        ticket_fit = max(0, 100 - diff*0.05)

    # distância (quanto mais perto, melhor)
    dist = distance_km(p)
    dist_fit = 100 if dist <= 20 else (80 if dist <= 100 else (60 if dist <= 300 else 40))

    # pesos (Pro vê o breakdown)
    return round(0.4*jacc + 0.3*stage_fit + 0.2*ticket_fit + 0.1*dist_fit), {
        "Tags": round(jacc),
        "Estágio": round(stage_fit),
        "Ticket": round(ticket_fit),
        "Distância": round(dist_fit),
    }

# ---------- page ----------
st.set_page_config(page_title="Explorar (Swipe)", page_icon="🔥", layout="centered")

st.markdown("""
<style>
.app-wrapper { max-width: 420px; margin: 0 auto; }
.card-icon { width: 100%; height: 220px; border-radius: 16px;
             background: linear-gradient(180deg, #f1f5f9, #e2e8f0);
             display:flex; align-items:center; justify-content:center;
             box-shadow: 0 8px 24px rgba(0,0,0,.08); margin-bottom:8px; }
.card-icon span { font-size: 110px; line-height: 1; }
.badges span{ margin-right: 6px; font-size: 12px; padding:3px 8px; border-radius:8px;
  background:#f2f4f7; border:1px solid #e5e7eb; }
.chip { display:inline-block; padding:4px 10px; margin:4px 6px 0 0; font-size:12px;
  border:1px solid #eaeaea; border-radius:999px; background:#fafafa; }
.meta, .distance, .small { color:#6b7280; font-size:13px; }
.comp-wrap { margin: 6px 0 4px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)
st.markdown("### 🔥 Explorar (Swipe)")

# info de likes restantes (Free)
if st.session_state.get("user_plan")!="Pro":
    reset_like_window_if_needed()
    rem = max(0, FREE_LIKES_PER_HOUR - st.session_state["likes_used"])
    mins = int((st.session_state["likes_reset_at"] - time.time())/60)+1
    st.caption(f"❤️ Likes restantes nesta hora: **{rem}** · reseta em ~{mins} min")

if not profiles:
    st.info("Sem perfis por enquanto.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

idx = st.session_state["swipe_idx"] % len(profiles)
p = profiles[idx]; pid = p.get("id", idx)

st.markdown(f'<div class="card-icon"><span>{icon_of(p)}</span></div>', unsafe_allow_html=True)
st.markdown('<div class="badges"><span>🛡️ Verificado</span><span>🟢 Online</span></div>', unsafe_allow_html=True)

headline = p.get("headline", "")
city = p.get("city", p.get("location","")); country = p.get("country","Brasil")
st.markdown(f"**{icon_of(p)} {p.get('name','')}**")
st.markdown(f'<div class="meta">{headline} • {city} • {country}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="small">Estágio: {p.get("stage","Seed")} · Rodada: ${p.get("raising",1500)}k · Ticket alvo: ${p.get("ticket_min",100)}k–${p.get("ticket_max",2000)}k</div>', unsafe_allow_html=True)
st.markdown(f'<div class="distance">~{distance_km(p)} km de você</div>', unsafe_allow_html=True)

score, breakdown = compat_score(p)
st.markdown(f'<div class="comp-wrap">Compatibilidade: <b>{score}%</b></div>', unsafe_allow_html=True)
st.progress(score)

with st.expander("Ver detalhes da compatibilidade (Pro)"):
    if st.session_state.get("user_plan")!="Pro":
        st.warning("🔒 Assine o Pro para ver o detalhe do score por dimensão (tags, estágio, ticket, distância).")
    else:
        for k,v in breakdown.items():
            st.write(f"{k}: {v}%")
            st.progress(v)

st.write(p.get("bio",""))
st.markdown("".join([f'<span class="chip">{t}</span>' for t in p.get("tags", [])]), unsafe_allow_html=True)

# ----- ações -----
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("❌", use_container_width=True, key=f"pass_{pid}"):
        st.session_state["history"].append(idx)
        st.session_state["passed"].add(pid)
        st.session_state["swipe_idx"] += 1
        st.rerun()
with c2:
    ok, rem = can_like()
    if st.button("💙", use_container_width=True, key=f"like_{pid}"):
        if not ok:
            st.error("Limite de likes nesta hora (Free). Tente novamente mais tarde ou assine o Pro.")
        else:
            if st.session_state.get("user_plan")!="Pro":
                st.session_state["likes_used"] += 1
            st.session_state["history"].append(idx)
            st.session_state["liked"].add(pid)
            if they_like_back(pid):
                st.session_state["matches"].add(pid)
                st.session_state["last_match_idx"] = pid
                st.session_state["last_match_name"] = p.get("name","")
                st.session_state["last_match_image"] = ""
                try: st.switch_page("pages/07_Match.py")
                except Exception: st.success("É um match! (demo)")
            else:
                st.session_state["swipe_idx"] += 1
                st.rerun()
with c3:
    if st.button("⭐", use_container_width=True, key=f"super_{pid}"):
        st.session_state["history"].append(idx)
        st.session_state["liked"].add(pid)
        st.session_state["matches"].add(pid)
        st.session_state["last_match_idx"] = pid
        st.session_state["last_match_name"] = p.get("name","")
        st.session_state["last_match_image"] = ""
        try: st.switch_page("pages/07_Match.py")
        except Exception: st.success("É um match! (Super Like demo)")

st.markdown("---")

# Pro: Rewind e Boost
if st.session_state.get("user_plan") == "Pro":
    colA, colB = st.columns(2)
    with colA:
        if st.button("⤺ Rewind (Pro)", use_container_width=True):
            if st.session_state["history"]:
                prev_idx = st.session_state["history"].pop()
                st.session_state["swipe_idx"] = prev_idx
                st.success("Última ação desfeita (demo).")
                st.rerun()
            else:
                st.info("Nada para desfazer ainda.")
    with colB:
        if st.button(f"🚀 Boost semanal (restam {st.session_state.get('boost_left',0)})", use_container_width=True):
            if st.session_state.get("boost_left",0)>0:
                st.session_state["boost_left"] -= 1
                st.success("Boost ativado por 24h! (simulação)")
            else:
                st.info("Sem Boost disponível no momento.")
else:
    st.info("🔓 No **Pro** você tem **Rewind** e **Boost** semanal.")

if st.button("💥 Forçar Match (demo)", key=f"force_{pid}"):
    st.session_state["matches"].add(pid)
    st.session_state["last_match_idx"] = pid
    st.session_state["last_match_name"] = p.get("name","")
    st.session_state["last_match_image"] = ""
    try: st.switch_page("pages/07_Match.py")
    except Exception: st.success("É um match! (forçado)")

st.markdown("</div>", unsafe_allow_html=True)
