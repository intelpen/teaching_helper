from pathlib import Path

import streamlit as st

from backend.admin_store import get_classes, is_admin_user


BASE_MENU_OPTIONS = [
    "Learning",
    "Mock Evaluation 1",
    "Mock Evaluation 2",
    "Feedback Survey",
]

ADMIN_MENU_OPTIONS = [
    "Manage Classes",
    "Manage users",
]


def render_sidebar():
    with st.sidebar:
        st.header("Virtual Assistant")
        user_info = st.session_state.get("user_info", {})
        user_email = user_info.get("email", "")
        user_name = user_info.get("name", "")
        selection_changed = False

        classes = get_classes()
        class_names = [class_obj["name"] for class_obj in classes]

        if not class_names:
            st.warning("No classes found.")
            st.session_state["pdf_file"] = None
        else:
            previous_class = st.session_state.get("selected_class_name")
            class_index = class_names.index(previous_class) if previous_class in class_names else 0
            selected_class_name = st.selectbox("Select Class", class_names, index=class_index)
            if previous_class is not None and selected_class_name != previous_class:
                selection_changed = True
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
                if previous_pdf is not None and selected_pdf != previous_pdf:
                    selection_changed = True
                st.session_state["pdf_file"] = selected_pdf
            else:
                if st.session_state.get("pdf_file") is not None:
                    selection_changed = True
                st.session_state["pdf_file"] = None
                st.info("No PDF uploaded for this class yet.")

        if selection_changed:
            st.session_state["active_page"] = "Learning"
            st.session_state["last_main_page"] = "Learning"
            st.session_state["main_menu_selection"] = "Learning"

        is_admin = is_admin_user(user_email)
        allowed_pages = list(BASE_MENU_OPTIONS) + (ADMIN_MENU_OPTIONS if is_admin else [])

        active_page = st.session_state.get("active_page", "Learning")
        if active_page == "Add a new Class":
            active_page = "Manage Classes"
            st.session_state["active_page"] = active_page
        if active_page not in allowed_pages:
            active_page = "Learning"
            st.session_state["active_page"] = active_page

        st.subheader("Main menu")
        last_main_page = st.session_state.get("last_main_page", "Learning")
        if last_main_page not in BASE_MENU_OPTIONS:
            last_main_page = "Learning"

        main_page_for_index = active_page if active_page in BASE_MENU_OPTIONS else last_main_page
        selected_main_page = st.radio(
            "Choose page",
            BASE_MENU_OPTIONS,
            index=BASE_MENU_OPTIONS.index(main_page_for_index),
            key="main_menu_selection",
        )
        main_page_changed = selected_main_page != last_main_page
        st.session_state["last_main_page"] = selected_main_page

        if active_page in BASE_MENU_OPTIONS or main_page_changed:
            st.session_state["active_page"] = selected_main_page
            active_page = selected_main_page

        if is_admin:
            st.subheader("Admin menu")
            if st.button("Manage Classes", use_container_width=True):
                st.session_state["active_page"] = "Manage Classes"
                active_page = "Manage Classes"
            if st.button("Manage users", use_container_width=True):
                st.session_state["active_page"] = "Manage users"
                active_page = "Manage users"

            if active_page in ADMIN_MENU_OPTIONS:
                st.caption(f"Current admin page: {active_page}")

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
