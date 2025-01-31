import streamlit as st
from backend.auth import authenticate_user, register_user
from frontend.sidebar import render_sidebar
from frontend.dialogs import render_dialog
from pathlib import Path
from streamlit_google_auth import Authenticate
import json
import os


# Main application interface

# Load the CSS file
def load_css(file_name):
    css_path = Path(file_name)
    if css_path.is_file():
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.error(f"CSS file '{file_name}' not found.")

# Main App Rendering
def render_main_app():
    st.set_page_config(page_title="Assisted Learning", page_icon="🤖", layout="wide")
    load_css("frontend/global.css")  # Load the CSS file

    config = json.load(open('backend/config.json', 'rt'))['GoogleAuth']

    st.session_state["authenticator"] = Authenticate(
        secret_credentials_path = config["client_secret"],
        cookie_name='teaching_helper',
        cookie_key='teaching_helper_key_secret',
        redirect_uri = os.getenv('redirect_uri') or 'http://localhost:8501',
    )

    # Catch the login event
    st.session_state["authenticator"].check_authentification()

    if st.session_state['connected']:
        st.sidebar.title("App Navigation")
        pdf_file = render_sidebar()
        render_dialog(pdf_file)
    else:
        # Create the login button
        st.session_state["authenticator"].login()


# Main routing logic

def main():
    render_main_app()

if __name__ == "__main__":
    main()
