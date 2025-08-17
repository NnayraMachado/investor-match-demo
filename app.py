import json, random, time
from pathlib import Path
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ---------- paths ----------
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
PROFILES_DIR = ASSETS_DIR / "profiles"
PHOTOS_DIR = ASSETS_DIR / "photos"
USER_DIR = ASSETS_DIR / "user"
PROFILES_JSON = ASSETS_DIR / "profiles.json"

USER_DIR.mkdir(parents=True, exist_ok=True)

# ---------- seed de dados ----------
NAMES = [
    ("Ana Souza","VC Early-Stage | Fintech", "São Paulo, SP", ["Fintech","SaaS B2B","Web3"]),
    ("Bruno Lima","Anjo | Agtech, Health", "Campinas, SP", ["Agtech","Health","Impacto"]),
    ("Carla Menezes","Family Office | Series A", "Rio de Janeiro, RJ", ["Energia","Infra","Logística"]),
    ("Diego Martins","Trader | Cripto & AI", "Curitiba, PR", ["Cripto","AI","DeFi"]),
    ("Elisa Rocha","Corporate Venture", "Belo Horizonte, MG", ["Indústria 4.0","IoT","Clima"]),
    ("Fernando Alves","Anjo | Marketplace", "Florianópolis, SC", ["Marketplace","E-commerce","Martech"]),
    ("Gabi Torres","VC | Consumer", "São Paulo, SP", ["Consumer","D2C","Creator Economy"]),
    ("Henrique Dias","PE Growth", "Porto Alegre, RS", ["Retail","Educação","SaaS"]),
]

# ---------- helpers de assets ----------
def _make_avatar(path: Path, initials: str):
    img = Image.new("RGB", (400, 400), (240, 240, 240))
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, 380, 380], fill=(200, 210, 255))
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 140)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), initials, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((400 - w) / 2, (400 - h) / 2), initials, fill=(30,30,60), font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)

def _list_photos():
    if not PHOTOS_DIR.exists(): return []
    exts = (".png",".jpg",".jpeg",".webp")
    return sorted([p for p in PHOTOS_DIR.iterdir() if p.suffix.lower() in exts], key=lambda p: p.name.lower())

def ensure_assets():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    if not PROFILES_JSON.exists():
        random.seed(7)
        photos = _list_photos()
        data = []
        for i,(name,headline,location,tags) in enumerate(NAMES, start=1):
            initials = "".join([p[0] for p in name.split()][:2]).upper()
            if i <= len(photos):
                img_rel = Path("assets")/"photos"/photos[i-1].name
            else:
                img_path = PROFILES_DIR/f"profile_{i}.png"
                _make_avatar(img_path, initials)
                img_rel = Path("assets")/"profiles"/f"profile_{i}.png"
            city = location.split(",")[0].strip()
            state = location.split(",")[1].strip() if "," in location else ""
            country = "Brasil"
            plan = random.choices(["Free","Pro"], weights=[0.75,0.25])[0]
            is_online = random.random() < 0.35
            last_seen_min = 0 if is_online else random.choice([5,15,35,60,180,720])
            is_new = i >= len(NAMES)-2
            likes_received = random.randint(3, 42)
            data.append({
                "id": i, "name": name, "headline": headline, "location": f"{city}, {state}",
                "country": country, "state": state, "city": city,
                "tags": tags, "bio": f"Interesses: {', '.join(tags)}. Ticket alvo: R$ {random.choice([200,300,500])}k - {random.choice([1,2,3])}M. Tese: {headline}.",
                "image": str(img_rel), "plan": plan, "is_online": is_online,
                "last_seen_min": last_seen_min, "is_new": is_new, "likes_received": likes_received
            })
        with open(PROFILES_JSON,"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)

def regenerate_profiles():
    if PROFILES_JSON.exists():
        PROFILES_JSON.unlink()
    ensure_assets()
    st.cache_data.clear()
    st.rerun()

ensure_assets()

# ---------- app ----------
st.set_page_config(page_title="Investor Match MVP", page_icon="💼")
st.session_state.setdefault("user_plan", "Free")
st.session_state.setdefault("my_tags", ["SaaS","Fintech"])
st.session_state.setdefault("my_name", "Você")

@st.cache_data
def load_profiles():
    with open(PROFILES_JSON,"r",encoding="utf-8") as f: 
        return json.load(f)
profiles = load_profiles()

# ---- mini motor de tendência (mock consistente) ----
@st.cache_data
def trend_last_3m(seed:int=123):
    random.seed(seed)
    base = 100
    series = []
    for _ in range(12):  # 12 semanas ~ 3 meses
        base += random.randint(-3, 6)  # viés leve de alta
        series.append(max(80, base))
    delta = series[-1] - series[0]
    label = "🔼 Otimista" if delta > 5 else ("➖ Moderado" if -5 <= delta <= 5 else "🔽 Cauteloso")
    insights = ["Fintech e SaaS em alta", "Cripto volátil, mas com interesse pontual", "Impacto/Clima estável"]
    return series, delta, label, insights

series, delta, label, insights = trend_last_3m()

def mini_trend_badge_for_profile(p: dict) -> str:
    """Gera um mini-badge de tendência por perfil com base em headline/tags."""
    text = (p.get("headline","") + " " + " ".join(p.get("tags",[]))).lower()
    if any(k in text for k in ["growth","series a","series b","saas","consumer","marketplace","ai"]):
        return "📈 Tendência: Crescimento"
    if any(k in text for k in ["infra","energia","logística","pe","private equity","family office"]):
        return "🛡️ Tendência: Defensivo"
    if any(k in text for k in ["cripto","web3","defi"]):
        return "⚠️ Tendência: Volátil"
    return "⏸️ Tendência: Moderado"

# ---------- sidebar (apenas para a DEMO no Streamlit) ----------
st.sidebar.title("Investor Match")
badge = "⭐ Pro" if st.session_state["user_plan"]=="Pro" else "Free"
st.sidebar.success(f"Plano: {badge}")
if "my_photo" in st.session_state and st.session_state["my_photo"]:
    st.sidebar.image(st.session_state["my_photo"], width=80, caption=st.session_state.get("my_name","Você"))
st.sidebar.page_link("pages/00_Apresentacao.py", label="Apresentação")
st.sidebar.page_link("pages/01_Perfil.py", label="Meu Perfil")
st.sidebar.page_link("pages/02_Swipe.py", label="Explorar (Swipe)")
st.sidebar.page_link("pages/03_Mensagens.py", label="Mensagens")
st.sidebar.page_link("pages/04_Assinatura.py", label="Assinatura Pro")
st.sidebar.page_link("pages/05_Admin_Demo.py", label="Admin (Demo)")
st.sidebar.page_link("pages/06_Feed.py", label="Feed de Updates (demo)")
st.sidebar.page_link("pages/07_Match.py", label="Tela de Match (teste)")
st.sidebar.page_link("pages/08_Tendencias.py", label="Tendências (demo)")
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Regerar perfis (usar fotos novas)"):
    regenerate_profiles()

# ---------- home ----------
_, mid, _ = st.columns([1,2,1])
with mid:
    st.markdown("### 💼 Investor Match — MVP")

    with st.container(border=True):
        # KPIs
        col1,col2,col3 = st.columns(3)
        with col1: st.metric("Usuários (demo)", "1.280")
        with col2: st.metric("Assinantes Pro (demo)", "214")
        with col3: st.metric("Taxa de Match (demo)", "18%")

        st.divider()

        # Tendência (geral) mini-card
        st.subheader("📈 Tendência do investidor (últ. 3m)")
        colt1, colt2 = st.columns([1,1])
        with colt1:
            st.caption(f"Sinal atual: **{label}**  |  Variação: **{('+' if delta>0 else '')}{delta} pts**")
            st.line_chart(series, height=120)
        with colt2:
            st.caption("Insights rápidos:")
            for tip in insights[:2]:
                st.write(f"• {tip}")
            st.page_link("pages/08_Tendencias.py", label="Abrir análises →")

        st.divider()

        # Destaques
        st.subheader("Perfis em destaque")
        for p in profiles[:2]:
            with st.container(border=True):
                # badges (Novo/Pro/Online)
                badges = []
                if p.get("is_new"): badges.append("🆕 Novo")
                if p.get("plan")=="Pro": badges.append("⭐ Pro")
                if p.get("is_online"): badges.append("🟢 Online")
                # mini badge de tendência por perfil
                badges.append(mini_trend_badge_for_profile(p))
                st.caption(" · ".join(badges))

                st.image(p["image"], use_container_width=True)
                st.markdown(f"**{p['name']}**")

                # ------ FALLBACK SEGURO PARA LOCALIZAÇÃO ------
                city = p.get("city") or p.get("location","").split(",")[0].strip()
                state = p.get("state") or (p.get("location","").split(",")[1].strip() if "," in p.get("location","") else "")
                country = p.get("country","Brasil")
                st.caption(f"{p['headline']} • {city}, {state} • {country}")
                # ------------------------------------------------

                st.write(p["bio"])

    st.info("Esta sidebar existe apenas para navegação da **DEMO** no Streamlit. No app final usamos tab bar/menu próprio.")
