import streamlit as st
import uuid


def init_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "current_id" not in st.session_state:
        st.session_state.current_id = None


def save_result(question, df, sql, schema):
    query_id = str(uuid.uuid4())

    st.session_state.history.insert(0, {
        "id": query_id,
        "question": question,
        "df": df,
        "sql": sql,
        "schema": schema
    })

    st.session_state.current_id = query_id


def get_current():
    for item in st.session_state.history:
        if item["id"] == st.session_state.current_id:
            return item
    return None
