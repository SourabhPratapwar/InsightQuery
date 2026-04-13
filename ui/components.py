import streamlit as st

def render_kpis(df):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📄 Rows", len(df))

    with col2:
        st.metric("📊 Columns", len(df.columns))

    with col3:
        numeric = df.select_dtypes(include="number")
        if not numeric.empty:
            st.metric("💰 Total", round(numeric.sum().sum(), 2))
        else:
            st.metric("💰 Total", "-")