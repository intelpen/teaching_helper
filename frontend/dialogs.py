import os
from pathlib import Path

import streamlit as st
from backend.admin_store import add_class, get_classes, get_users, is_admin_user, set_user_admin
from backend.chatbot import start_dialog, respond_to_query
from streamlit_pdf_viewer import pdf_viewer

# varianta
# def render_dialog():
#    st.header("Main Dialog Zone")
#    dialog_type = st.selectbox("Select Dialog Type", ["Learning", "Evaluation"])
#    user_input = st.text_input("Ask a question or start the dialog:")

#    if user_input:
#        response = respond_to_query(user_input, dialog_type)
#        st.write(response)

# varianta 3
# import streamlit as st
# from pathlib import Path

# def render_dialog(pdf_file):
#    left, right = st.columns([1, 2])  # Split the main dialog zone

# Left Zone: Display PDF in Browser Viewer
#    with left:
#        st.subheader("PDF Viewer")
#        if pdf_file:
#            st.markdown(
#                f'<iframe src="{pdf_file}" width="100%" height="700px"></iframe>',
#                unsafe_allow_html=True,
#            )
#        else:
#            st.info("No file selected. Select a course from the sidebar.")

# Right Zone: Chat Interface
#    with right:
#        st.subheader("Chat Interface")
#        dialog_type = st.selectbox("Select Dialog Type", ["Learning", "Evaluation"], key="dialog_type")
#        user_input = st.text_input("Ask a question or start the dialog:", key="user_input")

#        if user_input:
#            response = respond_to_query(user_input, dialog_type)
#            st.write(response)


# Mock Query Response
# def respond_to_query(query, dialog_type):
#    return f"Response to '{query}' in context of '{dialog_type}'."

#############################################################################################
# varianta doar cu functionalitate la Course 1, 2, ...
# import streamlit as st
# import base64
# from pathlib import Path

# def render_dialog(pdf_file):
#    left, right = st.columns([1, 2])  # Split the main dialog zone

# Left Zone: Display PDF Viewer
#    with left:
#        st.subheader("PDF Viewer")
#        if pdf_file:
#            try:
#                pdf_viewer(pdf_file)  # Updated function to serve PDF
#            except FileNotFoundError:
#                st.error(f"File {pdf_file} not found!")
#        else:
#            st.info("No file selected. Select a course from the sidebar.")

# Right Zone: Chat Interface
#    with right:
#        st.subheader("Chat Interface")
#        dialog_type = st.selectbox("Select Dialog Type", ["Learning", "Evaluation"], key="dialog_type")
#        user_input = st.text_input("Ask a question or start the dialog:", key="user_input")

#        if user_input:
#            response = respond_to_query(user_input, dialog_type)
#            st.write(response)


# Function to embed PDF in Streamlit
# def pdf_viewer(pdf_file):
#    with open(pdf_file, "rb") as f:
#        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
#    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700px"></iframe>'
#    st.markdown(pdf_display, unsafe_allow_html=True)


# Mock Query Response
# def respond_to_query(query, dialog_type):
#    return f"Response to '{query}' in context of '{dialog_type}'."


# incercare de functionalitate la Survey:

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# Generate and save the PDF
def generate_pdf(responses):
    os.makedirs("survey_completed_pdf", exist_ok=True)
    pdf_path = "survey_completed_pdf/completed_survey.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750
    c.drawString(100, y, "Survey Results")
    y -= 40
    for question, answer in responses.items():
        c.drawString(100, y, f"{question}: {answer}")
        y -= 20
        if y < 100:  # Start a new page if space runs out
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750
    c.save()
    return pdf_path


mock_evaluations = [
    # First evaluation - Basic SQL Concepts
    [
        {"type": "radio", "question": "1. Which of the following is NOT a basic SQL command?",
         "options": ["SELECT", "UPDATE", "MODIFY", "DELETE"]},
        {"type": "checkbox", "question": "2. Which of these are valid SQL data types? (Select all that apply)",
         "options": ["INTEGER", "VARCHAR", "BOOLEAN", "FLOAT", "STRING"]},
        {"type": "radio", "question": "3. What does DDL stand for in SQL?",
         "options": ["Data Definition Language", "Data Manipulation Language", "Database Definition Logic", "None of these"]},
        {"type": "radio", "question": "4. Which clause is used to filter rows in SQL?",
         "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"]},
        {"type": "checkbox", "question": "5. Which of these statements can be used to modify data in a database? (Select all that apply)",
         "options": ["INSERT", "UPDATE", "DELETE", "ALTER", "SELECT"]}
    ],
    # Second evaluation - Advanced SQL Topics
    [
        {"type": "radio", "question": "1. What is a foreign key?",
         "options": ["A key from another country", "A key that can access any table", "A field that links two tables", "A unique identifier"]},
        {"type": "checkbox", "question": "2. Which of these are types of JOIN in SQL? (Select all that apply)",
         "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "CROSS JOIN", "DIAGONAL JOIN"]},
        {"type": "radio", "question": "3. What is the purpose of HAVING clause?",
         "options": ["Filter groups", "Filter rows", "Sort results", "Join tables"]},
        {"type": "radio", "question": "4. Which statement is used to combine results from multiple SELECT statements?",
         "options": ["UNION", "JOIN", "MERGE", "COMBINE"]},
        {"type": "checkbox", "question": "5. Which of these are aggregate functions in SQL? (Select all that apply)",
         "options": ["COUNT", "SUM", "AVG", "MIN", "MEDIAN"]}
    ]
]


def render_mock_evaluation(eval_number):
    questions = mock_evaluations[eval_number]

    # Initialize session state for progress tracking
    if "mock_eval_state" not in st.session_state:
        st.session_state["mock_eval_state"] = {
            "current_question": 0,  # Tracks the current question index
            "responses": {},        # Stores the user's responses
            "completed": False,     # Indicates if the evaluation is completed
            "submitted": False      # Tracks if the submit button was clicked
        }

    eval_state = st.session_state["mock_eval_state"]
    current_question_index = eval_state["current_question"]
    responses = eval_state["responses"]

    # Layout for the evaluation: Left for questions, Right for responses
    left, right = st.columns([2, 1])

    # Left Column: Display the current question
    with left:
        if not eval_state["completed"]:
            if current_question_index < len(questions):
                question = questions[current_question_index]

                # Render the appropriate input type
                if question["type"] == "radio":
                    responses[question["question"]] = st.radio(
                        question["question"],
                        question["options"],
                        key=f"eval_q{current_question_index}"
                    )
                elif question["type"] == "checkbox":
                    responses[question["question"]] = st.multiselect(
                        question["question"],
                        question["options"],
                        default=responses.get(question["question"], []),
                        key=f"eval_q{current_question_index}"
                    )
                elif question["type"] == "text_conditional":
                    dependency = question["depends_on"]
                    condition = question["condition"]
                    if responses.get(dependency) == condition:
                        responses[question["question"]] = st.text_input(
                            question["question"],
                            value=responses.get(question["question"], ""),
                            key=f"eval_q{current_question_index}"
                        )

                # Add "Next" button with proper state handling
                next_button_key = f"eval_next_{current_question_index}"
                if st.button("Next", key=next_button_key):
                    # Increment the question index directly in session_state
                    st.session_state["mock_eval_state"]["current_question"] += 1
            else:
                # Mark evaluation as completed
                st.success(
                    "You have completed the evaluation! Click 'Submit' to generate the report.")
                eval_state["completed"] = True

        if eval_state["completed"] and not eval_state["submitted"]:
            if st.button("Submit", key="eval_submit"):
                pdf_path = generate_pdf(responses)
                st.session_state["eval_pdf_path"] = pdf_path
                eval_state["submitted"] = True

    # Right Column: Display responses so far
    with right:
        st.subheader("Your Responses So Far")
        for question, answer in responses.items():
            st.write(f"**{question}**: {answer}")

        # Display the completed PDF after submission
        if eval_state["submitted"] and st.session_state.get("eval_pdf_path"):
            st.subheader("Completed Evaluation")
            pdf_viewer(st.session_state["eval_pdf_path"])


def render_survey():
    # Define the survey questions
    survey = [
        {"type": "radio", "question": "1. What is your current level of education?",
         "options": ["High school", "Undergraduate", "Graduate", "Other (please specify):"]},
        {"type": "text_conditional", "question": "Other (please specify):",
         "depends_on": "1. What is your current level of education?", "condition": "Other (please specify):"},
        {"type": "radio", "question": "2. What is your primary field of study?",
         "options": ["Computer Science/IT", "Engineering", "Business", "Other (please specify):"]},
        {"type": "text_conditional", "question": "Other (please specify):",
         "depends_on": "2. What is your primary field of study?", "condition": "Other (please specify):"},
        {"type": "radio", "question": "3. Have you studied SQL or any database programming before?",
         "options": ["Yes", "No"]},
        {"type": "radio", "question": "4. How would you rate your current knowledge of SQL?",
         "options": ["Beginner", "Intermediate", "Advanced"]},
        {"type": "checkbox", "question": "5. How do you currently learn SQL?",
         "options": ["Classroom lectures", "Online courses", "Tutorials on websites", "Practicing on SQL platforms",
                     "Books or written material", "Other (please specify):"]},
        {"type": "text_conditional", "question": "Other (please specify):",
         "depends_on": "5. How do you currently learn SQL?", "condition": "Other (please specify):"},
    ]

    # Initialize session state for progress tracking
    if "survey_state" not in st.session_state:
        st.session_state["survey_state"] = {
            "current_question": 0,  # Tracks the current question index
            "responses": {},        # Stores the user's responses
            "completed": False,     # Indicates if the survey is completed
            "submitted": False      # Tracks if the submit button was clicked
        }

    survey_state = st.session_state["survey_state"]
    current_question_index = survey_state["current_question"]
    responses = survey_state["responses"]

    # Layout for the survey: Left for questions, Right for responses
    left, right = st.columns([2, 1])

    # Left Column: Display the current question
    with left:
        if not survey_state["completed"]:
            if current_question_index < len(survey):
                question = survey[current_question_index]

                # Render the appropriate input type
                if question["type"] == "radio":
                    responses[question["question"]] = st.radio(
                        question["question"],
                        question["options"],
                        key=f"q{current_question_index}"
                    )
                elif question["type"] == "checkbox":
                    responses[question["question"]] = st.multiselect(
                        question["question"],
                        question["options"],
                        default=responses.get(question["question"], []),
                        key=f"q{current_question_index}"
                    )
                elif question["type"] == "text_conditional":
                    dependency = question["depends_on"]
                    condition = question["condition"]
                    if responses.get(dependency) == condition:
                        responses[question["question"]] = st.text_input(
                            question["question"],
                            value=responses.get(question["question"], ""),
                            key=f"q{current_question_index}"
                        )

                # Add "Next" button with proper state handling
                next_button_key = f"next_{current_question_index}"
                if st.button("Next", key=next_button_key):
                    # Increment the question index directly in session_state
                    st.session_state["survey_state"]["current_question"] += 1
            else:
                # Mark survey as completed
                st.success(
                    "You have completed the survey! Click 'Submit' to generate the report.")
                survey_state["completed"] = True

        if survey_state["completed"] and not survey_state["submitted"]:
            if st.button("Submit"):
                pdf_path = generate_pdf(responses)
                st.session_state["survey_pdf_path"] = pdf_path
                survey_state["submitted"] = True

    # Right Column: Display responses so far
    with right:
        st.subheader("Your Responses So Far")
        for question, answer in responses.items():
            st.write(f"**{question}**: {answer}")

        # Display the completed PDF after submission
        if survey_state["submitted"] and st.session_state.get("survey_pdf_path"):
            st.subheader("Completed Survey")
            pdf_viewer(st.session_state["survey_pdf_path"])


# Generate the PDF with survey responses
def generate_pdf(responses):
    os.makedirs("survey_completed_pdf", exist_ok=True)
    pdf_path = "survey_completed_pdf/completed_survey.pdf"
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750
    c.drawString(100, y, "Survey Results")
    y -= 40
    for question, answer in responses.items():
        c.drawString(100, y, f"{question}: {answer}")
        y -= 20
        if y < 100:  # Start a new page if space runs out
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750
    c.save()
    return pdf_path


def render_add_class_page():
    st.title("Add a new Class")
    st.write("Create a class and optionally upload one or more PDF files.")

    with st.form("add_class_form", clear_on_submit=True):
        class_name = st.text_input("Class name")
        uploaded_files = st.file_uploader(
            "Upload class PDF files",
            type=["pdf"],
            accept_multiple_files=True,
        )
        submitted = st.form_submit_button("Create class")

    if submitted:
        try:
            new_class = add_class(class_name, uploaded_files or [])
            st.session_state["selected_class_name"] = new_class["name"]
            st.success(f"Class '{new_class['name']}' was created.")
            st.rerun()
        except ValueError as err:
            st.error(str(err))

    existing_classes = get_classes()
    if existing_classes:
        st.subheader("Existing classes")
        for class_obj in existing_classes:
            st.write(f"- {class_obj['name']} ({len(class_obj.get('pdfs', []))} PDFs)")


def render_manage_users_page():
    st.title("Manage users")
    st.write("Use the checkboxes to control admin access.")

    users = get_users()
    with st.form("manage_users_form"):
        admin_updates: dict[str, bool] = {}
        for user in users:
            email = user["email"]
            display_name = user.get("name", "").strip()
            label = f"{display_name} ({email})" if display_name else email
            admin_updates[email] = st.checkbox(
                label,
                value=bool(user.get("is_admin", False)),
                key=f"is_admin_{email}",
            )

        saved = st.form_submit_button("Save changes")

    if saved:
        for email, is_admin in admin_updates.items():
            set_user_admin(email, is_admin)
        st.success("User roles were updated.")
        st.rerun()


def render_dialog(pdf_file):
    if not st.session_state.get("connected", False):
        return

    active_page = st.session_state.get("active_page", "Learning")
    user_email = st.session_state.get("user_info", {}).get("email", "")
    admin_user = is_admin_user(user_email)

    if active_page == "Feedback Survey":
        st.title("Feedback Survey")
        render_survey()
        return

    if active_page == "Mock Evaluation 1":
        st.title("Mock Evaluation 1")
        render_mock_evaluation(0)
        return

    if active_page == "Mock Evaluation 2":
        st.title("Mock Evaluation 2")
        render_mock_evaluation(1)
        return

    if active_page == "Add a new Class":
        if not admin_user:
            st.error("Only admins can access this page.")
            return
        render_add_class_page()
        return

    if active_page == "Manage users":
        if not admin_user:
            st.error("Only admins can access this page.")
            return
        render_manage_users_page()
        return

    left, right = st.columns([0.6, 0.4])

    with left:
        selected_class_name = st.session_state.get("selected_class_name", "selected class")
        if pdf_file:
            st.subheader(f"Content for {selected_class_name}")
            if Path(pdf_file).exists():
                pdf_viewer(pdf_file)
            else:
                st.error("PDF file not found. Please check the file path.")
        else:
            st.info("No PDF selected. Please choose a class and a PDF from the sidebar.")

    with right:
        st.subheader("Chat Interface")
        dialog_type = st.selectbox(
            "Select Dialog Type",
            ["Learning", "Evaluation"],
            key="dialog_type",
        )
        user_input = st.text_input("Ask a question or start the dialog:", key="user_input")

        if user_input:
            response = respond_to_query(user_input, dialog_type)
            st.write(response)

# # Mock Query Response
# def respond_to_query(query, dialog_type):
#     return f"Response to '{query}' in context of '{dialog_type}'."
