import streamlit as st
from sidebar import render_sidebar
from dialogs import render_dialog

st.set_page_config(page_title="Learning & Evaluation App", layout="wide")


def main():
    st.sidebar.title("App Navigation")
    render_sidebar()
    render_dialog()


if __name__ == "__main__":
    main()
