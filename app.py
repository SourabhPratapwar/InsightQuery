import streamlit as st
import pandas as pd

from services.data_service import excel_to_db, load_schema
from services.query_service import run_query
from services.state_service import init_state, save_result, get_current

from rag import retrieve_relevant_schema
from ui.dashboard import render_chart
from llm import call_llm, generate_suggestions

DEFAULT_DB = "db.sqlite"

st.set_page_config(layout="wide")

# ---------------- FINAL UI STYLE ----------------
st.markdown("""
<style>

/* Background */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #1e293b, #020617);
}

/* REMOVE TOP SPACE */
.block-container {
    padding-top: 0rem !important;
    margin-top: -10px !important;
    max-width: 1100px;
    margin-left: auto;
    margin-right: auto;
}

/* Main Card */
.main-card {
    background: rgba(30, 41, 59, 0.55);
    border-radius: 20px;
    padding: 28px;
    border: 1px solid rgba(148,163,184,0.15);
    box-shadow: 0 20px 60px rgba(0,0,0,0.6);
}

/* Input */
.stTextInput input {
    height: 50px;
    border-radius: 12px;
    background: #1e293b;
    border: 1px solid #334155;
    color: white;
}

/* Run button */
.stButton>button {
    height: 50px;
    border-radius: 12px;
    background: linear-gradient(90deg, #3b82f6, #2563eb);
    color: white;
    border: none;
}

/* Suggestions */
button[kind="secondary"] {
    border-radius: 999px !important;
    padding: 8px 18px !important;
    background: #2563eb !important;
    color: white !important;
    border: none !important;
    margin-bottom: 10px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid rgba(148,163,184,0.1);
}

/* Divider */
hr {
    border: 1px solid rgba(148,163,184,0.1);
}

</style>
""", unsafe_allow_html=True)

# ---------------- INIT ----------------
init_state()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## InsightQuery")

uploaded = st.sidebar.file_uploader("Upload Data")
auto_fix = st.sidebar.toggle("Auto-fix SQL", True)
top_k = st.sidebar.slider("Schema Depth", 1, 10, 3)

st.sidebar.markdown("---")
st.sidebar.markdown("Recent Queries")

for item in st.session_state.history[:5]:
    st.sidebar.button(item["question"][:25], key=f"hist_{item['id']}")

# ---------------- DB ----------------
db_path = excel_to_db(uploaded) if uploaded else DEFAULT_DB
chunks, embeddings, relationships = load_schema(db_path)

# ---------------- MAIN CARD ----------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# HEADER
st.markdown("""
<div style="display:flex; align-items:center; gap:10px;">
    <div>
        <div style="font-size:26px; font-weight:600;">InsightQuery</div>
        <div style="color:#94a3b8;">Ask questions. Get insights instantly.</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="color:#94a3b8; margin-top:6px;">Text-to-SQL Data Query Engine</div>', unsafe_allow_html=True)

# INPUT
col1, col2 = st.columns([8, 2])

with col1:
    q = st.text_input(
        "",
        placeholder="Which cities have the highest average order value?",
        key="query_input",
        label_visibility="collapsed"
    )

with col2:
    run = st.button("Run", use_container_width=True)

# STATE
current = get_current()

# ---------------- SUGGESTIONS ----------------
if not current:

    st.markdown("### Suggested")

    suggestions = generate_suggestions(chunks)

    for i, s in enumerate(suggestions):
        if st.button(s, key=f"sug_{i}"):
            st.session_state.query_input = s

    st.markdown("<hr>", unsafe_allow_html=True)

# ---------------- RUN QUERY ----------------
if run and st.session_state.get("query_input"):

    q = st.session_state["query_input"]

    with st.spinner("Analyzing your data..."):
        schema = "\n".join(
            retrieve_relevant_schema(q, chunks, embeddings, top_k)
        )

        result = run_query(q, schema, db_path, auto_fix)

    if "error" in result:
        st.warning("Query failed")
        with st.expander("Details"):
            st.code(result["error"])
    else:
        save_result(q, result["df"], result["sql"], schema)

# ---------------- RESULTS ----------------
if current:
    df = current["df"].copy()

    st.markdown(f"### {current['question']}")
    st.caption(f"{len(df)} rows • {len(df.columns)} columns")

    render_chart(df, key="main_chart")

    st.divider()

    tabs = st.tabs(["Data", "SQL", "Insights"])

    with tabs[0]:
        st.dataframe(df, use_container_width=True)

    with tabs[1]:
        with st.expander("View SQL"):
            st.code(current["sql"], language="sql")

    with tabs[2]:
        if len(df) <= 50:
            try:
                with st.spinner("Generating insights..."):
                    ai_text = call_llm(f"Analyze:\n{df.head(20).to_dict()}")

                for line in ai_text.split("\n"):
                    if line.strip():
                        st.markdown(f"- {line}")

            except:
                st.warning("Insights unavailable")

st.markdown('</div>', unsafe_allow_html=True)