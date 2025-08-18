import streamlit as st
from pathlib import Path
import json, random

st.title("👤 Meu Perfil")
st.caption("Personalize seu perfil. Alguns itens são apenas para demonstração.")

# ---- CSS para avatar por ícone ----
st.markdown("""
<style>
.icon-avatar { width: 88px; height: 88px; border-radius: 50%;
               background:#eef2f7; display:flex; align-items:center; justify-content:center; }
.icon-avatar span { font-size: 44px; }
.icon-avatar.sm { width: 64px; height: 64px; }
.icon-avatar.sm span { font-size: 32px; }
</style>
""", unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"
USER_DIR = ASSETS_DIR / "user"
PROFILES_JSON = ASSETS_DIR / "profiles.json"
USER_DIR.mkdir(parents=True, exist_ok=True)

@st.cache_data
def load_profiles():
    with open(PROFILES_JSON,"r",encoding="utf-8") as f:
        data = json.load(f)
    # defaults para demo
    for p in data:
        p.setdefault("type","investor")
        p.setdefault("icon","💰" if p["type"]=="investor" else "🚀")
    return data

profiles = load_profiles()

# --- coordenadas simples por cidade ---
CITY_COORDS = {
    ("Brasil","SP","São Paulo"): (-23.5505, -46.6333),
    ("Brasil","SP","Campinas"): (-22.9056, -47.0608),
    ("Brasil","SP","Santos"): (-23.9608, -46.3336),
    ("Brasil","RJ","Rio de Janeiro"): (-22.9068, -43.1729),
    ("Brasil","RJ","Niterói"): (-22.8832, -43.1034),
    ("Brasil","MG","Belo Horizonte"): (-19.9245, -43.9352),
    ("Brasil","MG","Uberlândia"): (-18.9141, -48.2749),
    ("Brasil","PR","Curitiba"): (-25.4284, -49.2733),
    ("Brasil","PR","Londrina"): (-23.3045, -51.1696),
    ("Brasil","SC","Florianópolis"): (-27.5949, -48.5482),
    ("Brasil","SC","Joinville"): (-26.3044, -48.8487),
    ("Brasil","RS","Porto Alegre"): (-30.0346, -51.2177),
    ("Brasil","RS","Caxias do Sul"): (-29.1634, -51.1796),
    ("Portugal","Lisboa","Lisboa"): (38.7223, -9.1393),
    ("Portugal","Porto","Porto"): (41.1579, -8.6291),
    ("Estados Unidos","California","San Francisco"): (37.7749, -122.4194),
    ("Estados Unidos","California","Los Angeles"): (34.0522, -118.2437),
    ("Estados Unidos","New York","New York"): (40.7128, -74.0060),
}

# ---- foto do usuário (opcional) ----
with st.container(border=True):
    colL, colR = st.columns([1,2], vertical_alignment="center")
    with colL:
        st.markdown("**Foto do perfil (opcional)**")
        if st.session_state.get("my_photo"):
            st.image(st.session_state["my_photo"], width=140, caption=st.session_state.get("my_name","Você"))
        else:
            st.info("Sem foto. Você pode usar só o ícone 😉")
    with colR:
        up = st.file_uploader("Enviar/alterar foto (JPG/PNG/WebP)", type=["png","jpg","jpeg","webp"])
        if up is not None:
            ext = "." + up.name.split(".")[-1].lower()
            out = USER_DIR / f"me{ext}"
            for old in USER_DIR.glob("me.*"): old.unlink(missing_ok=True)
            out.write_bytes(up.read())
            st.session_state["my_photo"] = str(out.relative_to(BASE_DIR))
            st.success("Foto atualizada!")
            st.rerun()

# ---- localização (País/Estado/Cidade) ----
COUNTRIES = {
    "Brasil": {
        "SP": ["São Paulo", "Campinas", "Santos"],
        "RJ": ["Rio de Janeiro", "Niterói"],
        "MG": ["Belo Horizonte", "Uberlândia"],
        "PR": ["Curitiba", "Londrina"],
        "SC": ["Florianópolis", "Joinville"],
        "RS": ["Porto Alegre", "Caxias do Sul"],
    },
    "Portugal": {"Lisboa": ["Lisboa"], "Porto": ["Porto"]},
    "Estados Unidos": {"California": ["San Francisco","Los Angeles"], "New York": ["New York"]},
}

with st.form("perfil"):
    nome = st.text_input("Nome", st.session_state.get("my_name","Você"))
    headline = st.text_input("Headline", st.session_state.get("my_headline","Anjo | SaaS e Fintech"))
    bio = st.text_area("Bio / Tese", st.session_state.get("my_bio","Investidor anjo focado em SaaS B2B e Fintech."))
    pais = st.selectbox("País", list(COUNTRIES.keys()),
                        index=list(COUNTRIES.keys()).index(st.session_state.get("my_country","Brasil")))
    estados = list(COUNTRIES[pais].keys())
    estado = st.selectbox("Estado/Região", estados,
                          index=estados.index(st.session_state.get("my_state", estados[0])) if st.session_state.get("my_state") in estados else 0)
    cidades = COUNTRIES[pais][estado]
    cidade = st.selectbox("Cidade", cidades,
                          index=cidades.index(st.session_state.get("my_city", cidades[0])) if st.session_state.get("my_city") in cidades else 0)
    tags = st.multiselect(
        "Interesses",
        ["Fintech","SaaS","Health","Agtech","AI","Cripto","Clima","Educação","Web3","Marketplace","Consumer","D2C","IoT","Indústria 4.0","Impacto","Retail","Martech","Infra","Energia","Logística"],
        st.session_state.get("my_tags",["SaaS","Fintech"])
    )
    plano = st.selectbox("Plano", ["Free","Pro"], index=0 if st.session_state.get("user_plan","Free")=="Free" else 1)

    # escolha de ícone do usuário
    icon = st.selectbox("Seu ícone", ["🙂","💰","🚀","🧠","🏦","📈","🛠️","🧬","🌱","⚙️","🤖"],
                        index=1 if st.session_state.get("my_icon")=="💰" else 0)

    enviado = st.form_submit_button("Salvar (demo)")
    if enviado:
        st.session_state["my_name"] = nome
        st.session_state["my_headline"] = headline
        st.session_state["my_bio"] = bio
        st.session_state["my_country"] = pais
        st.session_state["my_state"] = estado
        st.session_state["my_city"] = cidade
        st.session_state["my_tags"] = tags
        st.session_state["user_plan"] = plano
        st.session_state["my_icon"] = icon

        # coordenadas
        latlon = CITY_COORDS.get((pais, estado, cidade))
        if latlon:
            st.session_state["my_lat"], st.session_state["my_lon"] = latlon
        st.success("Perfil salvo!")

# ---- preview do seu card ----
with st.container(border=True):
    st.markdown("**Preview do seu card**")
    badges = []
    if st.session_state.get("user_plan")=="Pro": badges.append("⭐ Pro")
    badges.append("🟢 Online")
    st.caption(" · ".join(badges))

    # mostra ícone (sempre) e foto (se existir) abaixo
    st.markdown(f'<div class="icon-avatar"><span>{st.session_state.get("my_icon","🙂")}</span></div>', unsafe_allow_html=True)
    if st.session_state.get("my_photo"):
        st.image(st.session_state["my_photo"], width=160, caption="Foto (opcional)")

    st.markdown(f"**{st.session_state.get('my_name','Você')}**")
    st.caption(f"{st.session_state.get('my_headline','')} • {st.session_state.get('my_city','')}, {st.session_state.get('my_state','')} • {st.session_state.get('my_country','')}")
    st.write(st.session_state.get("my_bio",""))

# ---- quem curtiu você (AGORA SÓ ÍCONES) ----
with st.container(border=True):
    st.markdown("**Quem curtiu você**")
    random.seed(99)
    likers = random.sample(profiles, k=min(4, len(profiles)))
    like_count = random.randint(8, 37)
    st.metric("Curtidas recebidas", like_count)

    if st.session_state.get("user_plan")!="Pro":
        st.warning("🔒 Torne-se **Pro** para ver quem curtiu seu perfil e acelerar os matches.")
    else:
        cols = st.columns(len(likers))
        for c, p in zip(cols, likers):
            with c:
                # SUBSTITUI a imagem pelo ícone
                icon = p.get("icon") or ("💰" if p.get("type")=="investor" else "🚀")
                st.markdown(f'<div class="icon-avatar sm"><span>{icon}</span></div>', unsafe_allow_html=True)
                st.caption(p["name"])
