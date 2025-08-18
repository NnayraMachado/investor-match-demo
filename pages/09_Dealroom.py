import streamlit as st
import pandas as pd
from pathlib import Path
import json, random, datetime as dt

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_FILE = BASE_DIR / "assets" / "profiles.json"

@st.cache_data
def load_profiles():
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

st.set_page_config(page_title="Dealroom", page_icon="📂", layout="centered")
st.title("📂 Dealroom do Match")

if st.session_state.get("user_plan")!="Pro":
    st.warning("🔒 Dealroom é um recurso **Pro**. Ative na aba **Assinatura**.")
    st.stop()

match_id = st.session_state.get("chat_with") or st.session_state.get("last_match_idx")
if not match_id:
    st.info("Abra um chat ou faça um match para acessar o Dealroom.")
    st.stop()

profiles = load_profiles()
other = next((x for x in profiles if x.get("id")==match_id), {"name":"Match"})
st.caption(f"Espaço compartilhado entre **Você** e **{other.get('name','Match')}**")

tab_files, tab_metrics, tab_check, tab_tasks, tab_integr = st.tabs(["📎 Arquivos", "📊 Métricas", "✅ Diligência", "🗒️ Tarefas", "🔌 Integrações (demo)"])

# --- arquivos ---
with tab_files:
    st.subheader("Arquivos")
    if "deal_files" not in st.session_state: st.session_state.deal_files = []
    up = st.file_uploader("Enviar arquivo (deck, planilha, etc.)", key="deal_up")
    if up:
        st.session_state.deal_files.append({"name": up.name, "size_kb": int(len(up.read())/1024), "when": dt.datetime.now().strftime("%d/%m %H:%M")})
        st.success("Arquivo adicionado (demo).")
    if st.session_state.deal_files:
        df = pd.DataFrame(st.session_state.deal_files)
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.info("Nenhum arquivo ainda.")

# --- métricas ---
with tab_metrics:
    st.subheader("Métricas de tração (demo)")
    if "deal_metrics" not in st.session_state:
        random.seed(7)
        months = pd.date_range(end=dt.date.today(), periods=6, freq="M")
        st.session_state.deal_metrics = pd.DataFrame({
            "Mês": months.strftime("%b/%Y"),
            "MRR (k USD)": [random.randint(20, 80) for _ in months],
            "Novos clientes": [random.randint(10, 60) for _ in months],
            "Churn (%)": [round(random.uniform(1.5, 6.5), 1) for _ in months],
        })
    st.dataframe(st.session_state.deal_metrics, use_container_width=True, hide_index=True)
    st.markdown("**MRR**"); st.line_chart(st.session_state.deal_metrics.set_index("Mês")["MRR (k USD)"])
    colA,colB = st.columns(2)
    with colA: st.markdown("**Novos clientes**"); st.bar_chart(st.session_state.deal_metrics.set_index("Mês")["Novos clientes"])
    with colB: st.markdown("**Churn**"); st.bar_chart(st.session_state.deal_metrics.set_index("Mês")["Churn (%)"])

# --- diligência ---
with tab_check:
    st.subheader("Checklist de Diligência")
    checks = st.session_state.setdefault("deal_checks", {
        "Documentos societários": False,
        "Cap table atualizado": False,
        "Balanço/PL": False,
        "Contratos relevantes": False,
        "Compliances/KYC": False,
    })
    for k,v in list(checks.items()):
        checks[k] = st.checkbox(k, value=v)
    if st.button("Marcar tudo", key="all_check"):
        for k in checks: checks[k] = True
        st.rerun()
    st.success("Checklist salvo (demo).")

# --- tarefas ---
with tab_tasks:
    st.subheader("Tarefas & Próximos passos")
    tasks = st.session_state.setdefault("deal_tasks", [])
    with st.form("new_task"):
        tdesc = st.text_input("Descrição da tarefa")
        who = st.selectbox("Responsável", ["Você","Outro(a)"])
        due = st.date_input("Prazo", value=dt.date.today()+dt.timedelta(days=7))
        sent = st.form_submit_button("Adicionar tarefa")
        if sent and tdesc.strip():
            tasks.append({"desc": tdesc.strip(), "who": who, "due": due.strftime("%d/%m/%Y"), "done": False})
            st.success("Tarefa adicionada (demo).")
            st.rerun()
    if tasks:
        for i,t in enumerate(tasks):
            cols = st.columns([0.1,2,1,1])
            with cols[0]: tasks[i]["done"] = st.checkbox("", value=t["done"], key=f"done_{i}")
            with cols[1]: st.write(t["desc"])
            with cols[2]: st.caption(t["who"])
            with cols[3]: st.caption(t["due"])
    else:
        st.info("Sem tarefas no momento.")

# --- integrações (demo) ---
with tab_integr:
    st.subheader("Integrações simuladas")
    st.toggle("Conectar Google Analytics", value=True)
    st.toggle("Conectar Stripe/Receita", value=False)
    st.toggle("Conectar CRM (RD/HubSpot)", value=False)
    st.info("Na versão Pro real, esses conectores trazem métricas automaticamente para o Dealroom.")
