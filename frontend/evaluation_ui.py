import streamlit as st
from backend.evaluation import calculate_score


def render_evaluation_ui():
    st.header("Evaluation Results")
    responses = [True, False, True]  # Dummy data
    score = calculate_score(responses)
    st.write(f"Your Score: {score}%")
