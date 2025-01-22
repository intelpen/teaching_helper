import streamlit as st
from backend.evaluation import evaluate_code_snippet

def render_sandbox():
    st.header("Code Sandbox")
    user_code = st.text_area("Enter your code here:")
    correct_code = "print('Hello, World!')"
    
    if st.button("Run Code"):
        result, feedback = evaluate_code_snippet(correct_code, user_code)
        st.write(feedback)
        if result:
            st.success("Correct Code!")
        else:
            st.error("Incorrect Code.")
