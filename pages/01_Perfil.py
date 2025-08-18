import streamlit as st
from pathlib import Path
import json, random

st.title("👤 Meu Perfil")
st.caption("Personalize seu perfil. Alguns itens são apenas para demonstração.")

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"
USER_DIR = ASSETS_DIR / "user"
PROFILES_JSON = ASSETS_DIR / "profiles.json"
USER_DIR.mkdir(parents=True, exist_ok=True)

@st.cache_data
def load_profiles():
    with open(PROFILES_JSON,"r",encoding="utf-8") as f:
        data = json.load(f)
    for p in data:
        p.setdefault("type","investor")
        p.setdefault("icon","💰" if p["type"]=="investor" else "🚀")
    return data

profiles = load_profiles()

# ---- foto do usuário ----
with st.container(border=True):
    colL, colR = st.columns([1,2], vertical_alignment="center")
    with colL:
        st.markdown("**Foto do perfil**")
        if st.session_state.get("my_photo"):
            st.image(st.session_state["my_photo"], width=140, caption=st.session_state.get("my_name","Você"))
        else:
            st.info("Sem foto ainda. Envie ao lado.")
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
    pais = st.selectbox("País", list(COUNTRIES.keys()), index=list(COUNTRIES.keys()).index(st.session_state.get("my_country","Brasil")))
    estados = list(COUNTRIES[pais].keys())
    estado = st.selectbox("Estado/Região", estados, index=estados.index(st.session_state.get("my_state", estados[0])) if st.session_state.get("my_state") in estados else 0)
    cidades = COUNTRIES[pais][estado]
    cidade = st.selectbox("Cidade", cidades, index=cidades.index(st.session_state.get("my_city", cidades[0])) if st.session_state.get("my_city") in cidades else 0)
    tags = st.multiselect(
        "Interesses",
        ["Fintech","SaaS","Health","Agtech","AI","Cripto","Clima","Educação","Web3","Marketplace","Consumer","D2C","IoT","Indústria 4.0","Impacto","Retail","Martech","Infra","Energia","Logística"],
        st.session_state.get("my_tags",["SaaS","Fintech"])
    )
    plano = st.selectbox("Plano", ["Free","Pro"], index=0 if st.session_state.get("user_plan","Free")=="Free" else 1)
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
        st.success("Perfil salvo!")

# ---- preview do seu card (como outros veem) ----
with st.container(border=True):
    st.markdown("**Preview do seu card**")
    badges = []
    if st.session_state.get("user_plan")=="Pro": badges.append("⭐ Pro")
    badges.append("🟢 Online")  # demo
    st.caption(" · ".join(badges))
    if st.session_state.get("my_photo"):
        st.markdown('<div class="card-img">', unsafe_allow_html=True)
        st.image(st.session_state["my_photo"], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    icon = "💰"  # demo
    st.markdown(f"**{icon} {st.session_state.get('my_name','Você')}**")
    st.caption(f"{st.session_state.get('my_headline','')} • {st.session_state.get('my_city','')}, {st.session_state.get('my_state','')} • {st.session_state.get('my_country','')}")
    st.write(st.session_state.get("my_bio",""))

# ---- pessoas que curtiram você (paywall) ----
with st.container(border=True):
    st.markdown("**Quem curtiu você**")
    random.seed(99)
    likers = random.sample(profiles, k=min(4, len(profiles)))
    like_count = random.randint(8, 37)
    st.metric("Curtidas recebidas", like_count)

    if st.session_state.get("user_plan")!="Pro":
        st.warning("🔒 Torne-se **Pro** para ver quem são as pessoas que curtiram seu perfil e acelerar os matches.")
    else:
        cols = st.columns(len(likers))
        for c, p in zip(cols, likers):
            with c:
                st.image(p["image"], width=80)
                st.caption(f"{p.get('icon','')} {p['name']}")
