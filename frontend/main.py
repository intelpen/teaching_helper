import streamlit as st
import json
import os
import requests
from pathlib import Path
from frontend.sidebar import render_sidebar
from frontend.dialogs import render_dialog
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Load the CSS file
def load_css(file_name):
    css_path = Path(file_name)
    if css_path.is_file():
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.error(f"CSS file '{file_name}' not found.")

def get_google_flow(config):
    # Read the actual client secret from the file
    try:
        with open(config['client_secret'], 'r') as secret_file:
            client_secret_data = json.load(secret_file)
                    
        return Flow.from_client_secrets_file(
            config['client_secret'],
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
            redirect_uri = os.getenv('redirect_uri') or 'http://localhost:8501',
        )
    except Exception as e:
        st.error(f"Error reading client secret: {e}")
        raise

def render_main_app():
    st.set_page_config(page_title="Assisted Learning", page_icon="🤖", layout="wide")
    load_css("frontend/global.css")

    # Load the OAuth configuration from backend/config.json
    config = json.load(open(json.load(open('backend/config.json', 'rt'))['GoogleAuth']['client_secret']))['web']
    config['client_secret'] = json.load(open('backend/config.json', 'rt'))['GoogleAuth']['client_secret']

    # Check if user credentials exist in session_state
    if "credentials" not in st.session_state:
        # See if we just got redirected back with an auth code
        query_params = st.query_params
        
        if "code" in query_params and query_params["code"]:
            try:
                code = query_params["code"][0] if isinstance(query_params["code"], list) else query_params["code"]
                flow = get_google_flow(config)
                try:
                    flow.fetch_token(code=code)
                    credentials = flow.credentials

                    userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
                    response = requests.get(userinfo_endpoint, headers={"Authorization": f"Bearer {credentials.token}"})
                    user_info = response.json()

                    st.session_state["user_info"] = user_info

                    st.session_state["credentials"] = {
                        "token": credentials.token,
                        "refresh_token": credentials.refresh_token,
                        "token_uri": credentials.token_uri,
                        "client_id": credentials.client_id,
                        "client_secret": credentials.client_secret,
                        "scopes": credentials.scopes,
                    }
                    st.session_state["connected"] = True  # Mark as connected when login is successful
                    # Clear query params and reload the app
                    st.query_params.clear()
                    st.rerun()
                
                except Exception as token_error:
                    st.error(f"Token retrieval failed: {token_error}")
                    st.session_state["connected"] = False  # Set to False on authentication failure
                    st.write("Please try logging in again.")
            
            except Exception as code_error:
                st.error(f"Authorization code processing failed: {code_error}")
                st.session_state["connected"] = False  # Set to False on authentication failure
        else:
            # Not logged in: create a login button that links to Google's OAuth 2.0 consent page.
            st.session_state["connected"] = False
            flow = get_google_flow(config)
            auth_url, state = flow.authorization_url(prompt="consent")
            st.session_state["state"] = state
            st.markdown(f'''
            <div style="display: flex; justify-content: center;">
                <a href="{auth_url}" target="_self">
                    <button style="
                        background-color: #4285F4;
                        border: none;
                        color: white;
                        padding: 10px 20px;
                        font-size: 18px;
                        border-radius: 5px;
                        cursor: pointer;">
                        Login with Google
                    </button>
                </a>
            </div>
            ''', unsafe_allow_html=True)
            return

    st.sidebar.title("App Navigation")
    pdf_file = render_sidebar()
    render_dialog(pdf_file)

# Main routing logic
def main():
    render_main_app()

if __name__ == "__main__":
    main()

