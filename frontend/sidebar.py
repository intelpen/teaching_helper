import streamlit as st

# initial
#def render_sidebar():
#    st.header("Assisted Learning")
#    st.selectbox("Select Chapter/Unit", ["Introduction", "Advanced Topics"])
#    st.subheader("Evaluation")
#    st.button("Evaluate Chapter")
#    st.subheader("Feedback Survey")
#    st.text_input("Provide Feedback")

# alta varianta
#def render_sidebar():
#    st.set_page_config(page_title="Assisted Learning", page_icon="🤖")
#    st.title("Virtual assistant")

#sidebar
#    with st.sidebar:
#        st.selectbox("Select Chapter/Unit", ["Introduction", "Advanced Topics"])
#        st.write("Make a choice")
#        st.subheader("Evaluation")
#        st.button("Evaluate Chapter")
#        st.subheader("Feedback Survey")
#        st.text_input("Provide Feedback")

# varianta 2
#def render_sidebar():
#    st.title("Virtual Assistant")
#    with st.sidebar:
#        st.selectbox("Select Chapter/Unit", ["Introduction", "Advanced Topics"], key="chapter_select")
#        st.write("Make a choice")
#        st.subheader("Evaluation")
#        st.button("Evaluate Chapter", key="evaluate_button")
#        st.subheader("Feedback Survey")
#        st.text_input("Provide Feedback", key="feedback_input")

#def render_dialog():
#    st.container()  # Wrap dialog content in a container for custom CSS targeting
#    st.header("Main Dialog Zone")
#    dialog_type = st.selectbox("Select Dialog Type", ["Learning", "Evaluation"], key="dialog_type")
#    user_input = st.text_input("Ask a question or start the dialog:", key="user_input")

#    if user_input:
#        response = respond_to_query(user_input, dialog_type)
#        st.write(response)

#def respond_to_query(query, dialog_type):
    # Mock function for demonstration
#    return f"Response to '{query}' in context of '{dialog_type}'."


def render_sidebar():
    st.title("Virtual Assistant")

    with st.sidebar:
        # Chapter selection dropdown
        st.selectbox("Select Chapter/Unit", ["Introduction", "Advanced Topics"], key="chapter_select")
        st.write("Make a choice")

        # Arrange buttons in rows of 3 for 12 files
        pdf_file = None  # Placeholder for the selected PDF file
        cols = st.columns(3)  # 3 buttons per row
        for i in range(1, 13):  # Loop for 12 files
            col = cols[(i - 1) % 3]
            with col:
                if st.button(f"Course {i}", key=f"course_button_{i}"):
                    st.session_state["pdf_file"] = f"data_pdf/course{i}.pdf"

        # Display the selected PDF file
        pdf_file = st.session_state.get("pdf_file", None)
        if pdf_file:
            st.write(f"Selected: {pdf_file}")

        # Evaluation section
        st.subheader("Evaluation")
        st.button("Evaluate Chapter")

        # Add Survey Button
        st.subheader("Feedback Survey")
        if st.button("Begin Survey"):
            st.session_state["survey_active"] = True  # Activate survey mode

        if st.session_state.get("connected", False):
            picture_url = st.session_state['user_info'].get('picture')
            if picture_url:
                st.image(picture_url)  # Explicitly check image loading
            st.write('Hello, '+ st.session_state['user_info'].get('name'))
            # st.write('Your email is '+ st.session_state['user_info'].get('email'))
            if st.button('Log out'):
                st.session_state.clear()  # Clear all session state data
                st.rerun()   # Rerun the app to reflect the logout state    # Return the selected PDF file path
    return pdf_file
