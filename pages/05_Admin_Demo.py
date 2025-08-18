import json, random
from pathlib import Path
import pandas as pd
import streamlit as st
from collections import Counter

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILES_JSON = BASE_DIR / "assets" / "profiles.json"

@st.cache_data
def load_profiles():
    with open(PROFILES_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

profiles = load_profiles()

# Atribui plano/status se faltarem
random.seed(42)
for p in profiles:
    p.setdefault("plan", random.choices(["Free", "Pro"], weights=[0.8, 0.2])[0])
    p.setdefault("status", random.choices(["Ativo", "Suspenso"], weights=[0.95, 0.05])[0])

def profiles_to_df(items):
    return pd.DataFrame([{
        "ID": p.get("id"), "Nome": p.get("name",""), "Headline": p.get("headline",""),
        "País": p.get("country",""), "Estado": p.get("state",""), "Cidade": p.get("city",""),
        "Tags": ", ".join(p.get("tags",[])), "Plano": p.get("plan"), "Status": p.get("status"),
        "Tipo": p.get("type","investor"), "Icone": p.get("icon","")
    } for p in items])

df_all = profiles_to_df(profiles)

st.set_page_config(page_title="Admin", page_icon="🛠️", layout="wide")
st.title("🛠️ Administrador (demonstração)")
st.caption("Painel organizado para gestão do app (dados fictícios).")

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Usuários (demo)", "1.280")
with col2: st.metric("Assinantes Pro (demo)", "214")
with col3: st.metric("Taxa de Match (demo)", "18%")
with col4: st.metric("Conversas ativas (demo)", "342")
st.divider()

tab_lista, tab_rel, tab_growth, tab_config = st.tabs(["📇 Usuários", "📊 Relatórios", "🚀 Top Growth (startups)", "⚙️ Configurações"])

# ---- Lista de usuários ----
with tab_lista:
    st.subheader("Gestão de perfis")
    c1,c2,c3,c4,c5 = st.columns([2,1.2,1.2,1.2,2])
    with c1: q = st.text_input("Buscar (nome/headline/cidade)", "")
    with c2: plan_filter = st.multiselect("Plano", ["Free","Pro"], [])
    with c3: status_filter = st.multiselect("Status", ["Ativo","Suspenso"], [])
    with c4: state_filter = st.multiselect("Estado", sorted({p.get("state","") for p in profiles if p.get("state")}), [])
    with c5:
        all_tags = sorted({t for p in profiles for t in p.get("tags",[])})
        tag_filter = st.multiselect("Tag", all_tags, [])

    dff = df_all.copy()
    if q.strip():
        ql=q.lower()
        mask = dff["Nome"].str.lower().str.contains(ql)|dff["Headline"].str.lower().str.contains(ql)|dff["Cidade"].str.lower().str.contains(ql)
        dff = dff[mask]
    if plan_filter: dff=dff[dff["Plano"].isin(plan_filter)]
    if status_filter: dff=dff[dff["Status"].isin(status_filter)]
    if state_filter: dff=dff[dff["Estado"].isin(state_filter)]
    if tag_filter: dff=dff[dff["Tags"].apply(lambda x: any(t in x for t in tag_filter))]

    st.caption(f"Resultados: {len(dff)}")

    colp1, colp2 = st.columns([1,3])
    with colp1: page_size = st.selectbox("Itens por página", [5,10,20], index=1)
    with colp2:
        total_pages = max(1, (len(dff) + page_size - 1)//page_size)
        page = st.number_input("Página", 1, total_pages, 1, 1)

    start = (page-1)*page_size; end = start+page_size
    page_df = dff.iloc[start:end].copy()
    page_df.insert(0,"Selecionar", False)

    edited = st.data_editor(
        page_df,
        column_config={"Selecionar": st.column_config.CheckboxColumn()},
        hide_index=True, disabled=[c for c in page_df.columns if c!="Selecionar"],
        use_container_width=True, height=360
    )

    b1,b2,b3 = st.columns(3)
    with b1:
        if st.button("🚫 Suspender (demo)"):
            n=int(edited["Selecionar"].sum())
            st.success(f"{n} perfis seriam suspensos (demonstração).") if n else st.warning("Selecione pelo menos 1 perfil.")
    with b2:
        if st.button("✅ Reativar (demo)"):
            n=int(edited["Selecionar"].sum())
            st.success(f"{n} perfis seriam reativados (demonstração).") if n else st.warning("Selecione pelo menos 1 perfil.")
    with b3:
        csv = dff.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar CSV (filtro atual)", csv, "usuarios_filtrados.csv", "text/csv")

# ---- Relatórios rápidos ----
with tab_rel:
    st.subheader("Relatórios rápidos (demo)")
    tag_counts = Counter(t for p in profiles for t in p.get("tags",[]))
    top_tags = (pd.DataFrame(tag_counts.most_common(8), columns=["Tag", "Contagem"])
                .set_index("Tag"))
    st.markdown("**Top interesses**"); st.bar_chart(top_tags)
    colr1,colr2 = st.columns(2)
    with colr1:
        by_plan = (pd.Series([p.get("plan","Free") for p in profiles])
                   .value_counts().rename_axis("Plano").to_frame("Qtd"))
        st.markdown("**Distribuição por Plano**"); st.bar_chart(by_plan)
    with colr2:
        by_state = (pd.Series([p.get("state","") for p in profiles if p.get("state")])
                    .value_counts().head(10).rename_axis("Estado").to_frame("Qtd"))
        st.markdown("**Top Estados**"); st.bar_chart(by_state)

# ---- Top Growth (startups) ----
with tab_growth:
    st.subheader("🚀 Startups com melhor crescimento (com base em `metrics`)")
    rows = []
    for p in profiles:
        if p.get("type") == "startup" and isinstance(p.get("metrics"), dict):
            rows.append({
                "Icone": p.get("icon","🚀"),
                "Startup": p.get("name",""),
                "Setores": ", ".join(p.get("tags",[])),
                "Growth (%)": int(100 * p["metrics"].get("growth_rate", 0)),
                "Churn (%)": int(100 * p["metrics"].get("churn", 0)),
                "MRR (USD)": p["metrics"].get("MRR", 0),
                "Estágio": p.get("stage","Seed"),
                "Cidade": p.get("city","")
            })
    if rows:
        df = (pd.DataFrame(rows)
                .sort_values(["Growth (%)","MRR (USD)"], ascending=False)
                .reset_index(drop=True))
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar CSV", csv, "top_growth_startups.csv", "text/csv")
    else:
        st.info("Nenhuma startup com `metrics` definida no profiles.json ainda.")

# ---- Configurações ----
with tab_config:
    st.subheader("Configurações rápidas (demonstração)")
    st.toggle("Revisão manual de novos perfis", value=True)
    st.toggle("Notificar matches por e-mail", value=True)
    st.toggle("Ativar Boost semanal", value=False)
    st.selectbox("Janela de suporte", ["Horário comercial","24/7"], index=0)
    st.info("Opções ilustrativas no MVP demo.")
