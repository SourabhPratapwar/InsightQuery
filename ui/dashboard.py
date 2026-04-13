import streamlit as st


def render_chart(df, key):
    numeric = df.select_dtypes(include="number").columns
    cols = df.columns

    if len(cols) < 2:
        st.info("Not enough data to visualize")
        return

    x = cols[0]
    y = cols[1]

    chart_type = st.selectbox(
        "Select Chart Type",
        ["Bar", "Line"],
        key=key
    )

    st.markdown(f"**X:** {x} | **Y:** {y}")

    if chart_type == "Line":
        st.line_chart(df, x=x, y=y)
    else:
        st.bar_chart(df, x=x, y=y)
