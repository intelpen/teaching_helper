import streamlit as st
from backend.auth import authenticate_user, register_user
from frontend.sidebar import render_sidebar
from frontend.dialogs import render_dialog

# Function to handle login


def render_login():
    st.title("Login to the App")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(email, password):
            st.success("Login successful!")
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            st.rerun()  # Refresh to load the main app
        else:
            st.error("Invalid email or password.")

# Function to handle registration


def render_register():
    st.title("Register for the App")
    st.text('Registering is disabled. Send an email to adrian.balan@airl.ro register')

    # email = st.text_input("Email")
    # password = st.text_input("Password", type="password")

    # if st.button("Register"):
    #     try:
    #         register_user(email, password)
    #         st.success("Registration successful! Please log in.")
    #     except Exception as e:
    #         st.error(f"Registration failed: {e}")

# Main application interface


def render_main_app():
    st.sidebar.title("App Navigation")
    render_sidebar()
    render_dialog()

# Main routing logic


def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        render_main_app()
    else:
        choice = st.radio("Choose an option:", ["Login", "Register"])
        if choice == "Login":
            render_login()
        elif choice == "Register":
            render_register()


if __name__ == "__main__":
    main()
