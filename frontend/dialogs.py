import streamlit as st
from backend.chatbot import start_dialog, respond_to_query

def render_dialog():
    st.header("Main Dialog Zone")
    dialog_type = st.selectbox("Select Dialog Type", ["Learning", "Evaluation"])
    user_input = st.text_input("Ask a question or start the dialog:")
    
    if user_input:
        response = respond_to_query(user_input, dialog_type)
        st.write(response)
