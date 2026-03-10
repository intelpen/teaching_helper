import streamlit as st
import json
import os
import requests
import secrets
import hashlib
import base64
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

def get_google_flow(config, state=None, code_verifier=None):
    # Read the actual client secret from the file
    try:
        with open(config['client_secret'], 'r') as secret_file:
            client_secret_data = json.load(secret_file)
                    
        flow = Flow.from_client_secrets_file(
            config['client_secret'],
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
            state=state,
            redirect_uri = os.getenv('redirect_uri') or 'http://localhost:8501',
        )
        # Preserve PKCE verifier across reruns/callback if the library enables PKCE.
        if code_verifier:
            flow.code_verifier = code_verifier
        return flow
    except Exception as e:
        st.error(f"Error reading client secret: {e}")
        raise

def build_code_verifier(oauth_state):
    # Build a deterministic PKCE verifier from state so callback can reconstruct it even if session_state is lost.
    digest = hashlib.sha256(f"teaching-helper-pkce:{oauth_state}".encode("utf-8")).digest()
    verifier = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    return verifier

def render_main_app():
    st.set_page_config(page_title="Assisted Learning", page_icon="🤖", layout="wide")
    load_css("frontend/global.css")

    # Load the OAuth configuration from backend/config.json
    config = json.load(open(json.load(open('backend/config.json', 'rt'))['GoogleAuth']['client_secret']))['web']
    config['client_secret'] = json.load(open('backend/config.json', 'rt'))['GoogleAuth']['client_secret']

    def _first_query_param_value(query_params, key):
        value = query_params.get(key)
        if isinstance(value, list):
            return value[0] if value else None
        return value

    # Check if user credentials exist in session_state
    if "credentials" not in st.session_state:
        # See if we just got redirected back with an auth code
        query_params = st.query_params
        callback_error = st.session_state.pop("oauth_error", None)
        if callback_error:
            st.error(callback_error)

        if "code" in query_params and query_params["code"]:
            try:
                code = _first_query_param_value(query_params, "code")
                returned_state = _first_query_param_value(query_params, "state")
                expected_state = st.session_state.get("oauth_state")

                if expected_state and returned_state and expected_state != returned_state:
                    st.session_state["oauth_error"] = "Login failed: OAuth state mismatch. Please try logging in again."
                    st.query_params.clear()
                    st.rerun()

                if st.session_state.get("oauth_code_used") == code:
                    st.session_state["oauth_error"] = "Login session expired. Please try logging in again."
                    st.query_params.clear()
                    st.rerun()

                expected_code_verifier = build_code_verifier(returned_state) if returned_state else st.session_state.get("oauth_code_verifier")
                flow = get_google_flow(
                    config,
                    state=returned_state or expected_state,
                    code_verifier=expected_code_verifier,
                )
                try:
                    flow.fetch_token(code=code)
                    st.session_state["oauth_code_used"] = code
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
                    st.session_state.pop("oauth_state", None)
                    st.session_state.pop("oauth_code_verifier", None)
                    st.query_params.clear()
                    st.rerun()
                
                except Exception as token_error:
                    st.session_state["connected"] = False  # Set to False on authentication failure
                    st.session_state["oauth_code_used"] = code
                    st.session_state["oauth_error"] = f"Token retrieval failed: {token_error}"
                    st.session_state.pop("oauth_code_verifier", None)
                    st.query_params.clear()
                    st.rerun()
            
            except Exception as code_error:
                st.session_state["connected"] = False  # Set to False on authentication failure
                st.session_state["oauth_error"] = f"Authorization code processing failed: {code_error}"
                st.query_params.clear()
                st.rerun()
        else:
            # Not logged in: create a login button that links to Google's OAuth 2.0 consent page.
            st.session_state["connected"] = False
            state = secrets.token_urlsafe(32)
            code_verifier = build_code_verifier(state)
            flow = get_google_flow(config, state=state, code_verifier=code_verifier)
            auth_url, state = flow.authorization_url(
                prompt="consent",
                access_type="offline",
                state=state,
            )
            st.session_state["oauth_state"] = state
            st.session_state["oauth_code_verifier"] = code_verifier
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
            <div style="display: flex; justify-content: center;">
                To get access please send an email with the desired role (instructor/student) and affiliafion:
            </div>
            ''', unsafe_allow_html=True)
            st.columns(3)[1].image('frontend/email.png', width=170)
            return

    st.sidebar.title("App Navigation")
    pdf_file = render_sidebar()
    render_dialog(pdf_file)

# Main routing logic
def main():
    render_main_app()

if __name__ == "__main__":
    main()
