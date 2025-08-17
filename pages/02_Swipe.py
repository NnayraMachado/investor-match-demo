import json, random
from secrets import randbelow
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILES_JSON = BASE_DIR / "assets" / "profiles.json"

@st.cache_data
def load_profiles():
    with open(PROFILES_JSON, "r", encoding="utf-8") as f:
        return json.load(f)
profiles = load_profiles()

# ---- estado ----
st.session_state.setdefault("current_index", 0)
st.session_state.setdefault("matches", set())
st.session_state.setdefault("liked", set())
st.session_state.setdefault("passed", set())
st.session_state.setdefault("user_plan", "Free")
st.session_state.setdefault("last_anim", "right")
st.session_state.setdefault("filter_tags", [])
st.session_state.setdefault("filter_country", None)
st.session_state.setdefault("filter_state", None)
st.session_state.setdefault("filter_city", None)
st.session_state.setdefault("boost_on", False)

# define pitch demo nos dois primeiros
for i, p in enumerate(profiles[:2], start=1):
    p.setdefault("pitch_url", "https://www.youtube.com/embed/jfKfPfyJRdk")
for p in profiles[2:]:
    p.setdefault("pitch_url", None)

# ---- simulador de like recíproco (estável por perfil) ----
def they_like_back(profile_id: int) -> bool:
    key = f"likeback_{profile_id}"
    if key not in st.session_state:
        st.session_state[key] = randbelow(100) < 30  # 30% de chance
    return st.session_state[key]

# ---- filtros (Pro) ----
_, mid, _ = st.columns([1,2,1])
with mid:
    st.markdown("### 🔥 Explorar (Swipe)")
    with st.expander("🎯 Filtros (Pro)", expanded=False):
        disabled = st.session_state["user_plan"] != "Pro"
        if disabled:
            st.info("Disponível no **Pro**. Ative em Assinatura para usar filtros avançados e geográficos.")
        # tags
        all_tags = sorted({t for p in profiles for t in p["tags"]})
        sel_tags = st.multiselect("Tópicos de interesse", all_tags, st.session_state["filter_tags"], disabled=disabled)
        # geográfico
        countries = sorted({p.get("country","Brasil") for p in profiles})
        country = st.selectbox("País", ["(qualquer)"]+countries, index=0, disabled=disabled)
        states = sorted({p.get("state","") for p in profiles if (country=="(qualquer)" or p.get("country")==country)})
        state = st.selectbox("Estado/Região", ["(qualquer)"]+[s for s in states if s], index=0, disabled=disabled)
        cities = sorted({p.get("city","") for p in profiles if ((country=="(qualquer)" or p.get("country")==country) and (state=="(qualquer)" or p.get("state")==state))})
        city = st.selectbox("Cidade", ["(qualquer)"]+[c for c in cities if c], index=0, disabled=disabled)

        if not disabled:
            st.session_state["filter_tags"] = sel_tags
            st.session_state["filter_country"] = None if country=="(qualquer)" else country
            st.session_state["filter_state"] = None if state=="(qualquer)" else state
            st.session_state["filter_city"] = None if city=="(qualquer)" else city

def pass_geo_filters(p):
    c = st.session_state["filter_country"]
    s = st.session_state["filter_state"]
    ci = st.session_state["filter_city"]
    if c and p.get("country")!=c: return False
    if s and p.get("state")!=s: return False
    if ci and p.get("city")!=ci: return False
    return True

def filtered_indices():
    tags = st.session_state["filter_tags"]
    idxs = []
    for i, p in enumerate(profiles):
        cond_geo = pass_geo_filters(p) if st.session_state["user_plan"]=="Pro" else True
        cond_tag = (st.session_state["user_plan"]!="Pro") or (not tags) or any(t in tags for t in p["tags"])
        if cond_geo and cond_tag: idxs.append(i)
    return idxs or list(range(len(profiles)))

def get_current_card():
    idxs = filtered_indices()
    pos = st.session_state["current_index"] % len(idxs)
    return profiles[idxs[pos]], idxs[pos]

def next_profile(direction="right"):
    st.session_state["current_index"] += 1
    st.session_state["last_anim"] = direction

def rewind():
    st.session_state["current_index"] = max(st.session_state["current_index"] - 1, 0)
    st.session_state["last_anim"] = "left"

# ---- css leve ----
st.markdown("""
<style>
.card img { width: 100%; border-radius: 12px; display:block; }
.slide-in-right { animation: slideInRight 260ms ease-out; }
.slide-in-left  { animation: slideInLeft 260ms ease-out; }
@keyframes slideInRight { from {transform: translateX(24px); opacity: 0;} to {transform: translateX(0); opacity: 1;} }
@keyframes slideInLeft  { from {transform: translateX(-24px); opacity: 0;} to {transform: translateX(0); opacity: 1;} }
.chip { display:inline-block; padding:4px 10px; margin:4px 6px 0 0; font-size:12px; border:1px solid #eaeaea; border-radius:999px; background:#fafafa; }
.comp-wrap { margin: 6px 0 2px 0; }
.badges span { margin-right: 6px; font-size: 12px; padding:3px 8px; border-radius:8px; background:#f2f4f7; border:1px solid #e5e7eb;}
.trend { font-size:12px; padding:4px 8px; border:1px solid #e5e7eb; border-radius:8px; background:#f9fafb; display:inline-block; margin-bottom:8px;}
</style>
""", unsafe_allow_html=True)

# ---- card atual ----
card, real_idx = get_current_card()
anim = "slide-in-right" if st.session_state["last_anim"] == "right" else "slide-in-left"

with mid:
    with st.container(border=True):
        # badges
        b = []
        if card.get("is_new"): b.append("🆕 Novo")
        if card.get("plan")=="Pro": b.append("⭐ Pro")
        if card.get("is_online"): b.append("🟢 Online")
        if b: st.markdown('<div class="badges">'+" ".join([f"<span>{x}</span>" for x in b])+"</div>", unsafe_allow_html=True)

        st.markdown(f'<div class="card {anim}">', unsafe_allow_html=True)
        st.image(card["image"], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"**{card['name']}**")
        st.caption(f"{card['headline']} • {card.get('city','')}, {card.get('state','')} • {card.get('country','')}")

        # compatibilidade (% + barra)
        my_tags = set(t.lower() for t in st.session_state.get("my_tags", ["SaaS","Fintech"]))
        their = set(t.lower() for t in card["tags"])
        jacc = 0 if not (my_tags | their) else round(100*len(my_tags & their)/len(my_tags | their))
        st.markdown(f'<div class="comp-wrap">Compatibilidade: **{jacc}%**</div>', unsafe_allow_html=True)
        st.progress(jacc)

        # tendência por perfil (leitura rápida)
        trend_label = "🔼 foco em crescimento" if "SaaS" in card["headline"] or "Growth" in card["headline"] else ("🔽 postura defensiva" if "PE" in card["headline"] or "Infra" in card["headline"] else "➖ moderado")
        st.markdown(f'<span class="trend">Tendência do perfil: {trend_label}</span>', unsafe_allow_html=True)

        # pitch oculto
        if card.get("pitch_url"):
            show_pitch = st.checkbox("▶️ Ver pitch (1 min)", key=f"show_pitch_{real_idx}")
            if show_pitch: st.video(card["pitch_url"])

        st.write(card["bio"])
        st.markdown("".join([f'<span class="chip">{t}</span>' for t in card["tags"]]), unsafe_allow_html=True)

        # botões
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1:
            if st.button("⏪", help="Rewind (Pro)", disabled=(st.session_state["user_plan"]!="Pro")):
                rewind(); st.rerun()
        with c2:
            if st.button("❌", help="Passar"):
                st.session_state["passed"].add(real_idx)
                next_profile("left"); st.rerun()
        with c3:
            if st.button("💙", help="Curtir"):
                st.session_state["liked"].add(real_idx)
                if they_like_back(real_idx):   # ✅ só vira match se houver like recíproco
                    st.session_state["matches"].add(real_idx)
                    st.session_state["last_match_idx"] = real_idx
                    st.session_state["last_match_name"] = card["name"]
                    st.session_state["last_match_image"] = card["image"]
                    st.switch_page("pages/07_Match.py")
                else:
                    next_profile("right"); st.rerun()
        with c4:
            if st.button("⭐", help="Super Like (Pro)", disabled=(st.session_state["user_plan"]!="Pro")):
                st.session_state["liked"].add(real_idx)
                st.session_state["matches"].add(real_idx)
                st.session_state["last_match_idx"] = real_idx
                st.session_state["last_match_name"] = card["name"]
                st.session_state["last_match_image"] = card["image"]
                st.switch_page("pages/07_Match.py")
        with c5:
            if st.button("🚀", help="Boost (demo)"):
                st.session_state["boost_on"] = not st.session_state["boost_on"]; st.rerun()

    st.markdown("---")
    if st.button("💥 Forçar Match (demo)"):
        st.session_state["matches"].add(real_idx)
        st.session_state["last_match_idx"] = real_idx
        st.session_state["last_match_name"] = card["name"]
        st.session_state["last_match_image"] = card["image"]
        st.switch_page("pages/07_Match.py")
