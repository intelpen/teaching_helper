import streamlit as st


def render_sidebar():
    st.header("Assisted Learning")
    st.selectbox("Select Chapter/Unit", ["Introduction", "Advanced Topics"])
    st.subheader("Evaluation")
    st.button("Evaluate Chapter")
    st.subheader("Feedback Survey")
    st.text_input("Provide Feedback")
