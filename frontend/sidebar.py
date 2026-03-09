from pathlib import Path

import streamlit as st

from backend.admin_store import get_classes, is_admin_user


BASE_MENU_OPTIONS = [
    "Learning",
    "Mock Evaluation 1",
    "Mock Evaluation 2",
    "Feedback Survey",
]


def render_sidebar():
    with st.sidebar:
        st.header("Virtual Assistant")
        user_info = st.session_state.get("user_info", {})
        user_email = user_info.get("email", "")
        user_name = user_info.get("name", "")

        classes = get_classes()
        class_names = [class_obj["name"] for class_obj in classes]

        if not class_names:
            st.warning("No classes found.")
            st.session_state["pdf_file"] = None
        else:
            previous_class = st.session_state.get("selected_class_name")
            class_index = class_names.index(previous_class) if previous_class in class_names else 0
            selected_class_name = st.selectbox("Select Class", class_names, index=class_index)
            st.session_state["selected_class_name"] = selected_class_name

            selected_class = next(
                class_obj for class_obj in classes if class_obj["name"] == selected_class_name
            )
            st.session_state["selected_class_id"] = selected_class["id"]

            class_pdfs = selected_class.get("pdfs", [])
            if class_pdfs:
                previous_pdf = st.session_state.get("pdf_file")
                pdf_index = class_pdfs.index(previous_pdf) if previous_pdf in class_pdfs else 0
                selected_pdf = st.selectbox(
                    "Select Class PDF",
                    class_pdfs,
                    index=pdf_index,
                    format_func=lambda value: Path(value).name,
                )
                st.session_state["pdf_file"] = selected_pdf
            else:
                st.session_state["pdf_file"] = None
                st.info("No PDF uploaded for this class yet.")

        menu_options = list(BASE_MENU_OPTIONS)
        if is_admin_user(user_email):
            menu_options.extend(["Add a new Class", "Manage users"])

        previous_page = st.session_state.get("active_page", "Learning")
        if previous_page not in menu_options:
            previous_page = "Learning"

        selected_page = st.radio("Menu", menu_options, index=menu_options.index(previous_page))
        st.session_state["active_page"] = selected_page

        if st.session_state.get("connected", False):
            picture_url = user_info.get("picture")
            if picture_url:
                st.image(picture_url)

            display_name = user_name or user_email or "User"
            st.write(f"Hello, {display_name}")
            if st.button("Log out"):
                st.session_state.clear()
                st.rerun()

    return st.session_state.get("pdf_file")
