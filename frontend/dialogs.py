import streamlit as st
from backend.chatbot import start_dialog, respond_to_query
from streamlit_pdf_viewer import pdf_viewer

# varianta
#def render_dialog():
#    st.header("Main Dialog Zone")
#    dialog_type = st.selectbox("Select Dialog Type", ["Learning", "Evaluation"])
#    user_input = st.text_input("Ask a question or start the dialog:")

#    if user_input:
#        response = respond_to_query(user_input, dialog_type)
#        st.write(response)

#varianta 3
#import streamlit as st
#from pathlib import Path

#def render_dialog(pdf_file):
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
#def respond_to_query(query, dialog_type):
#    return f"Response to '{query}' in context of '{dialog_type}'."

#############################################################################################
# varianta doar cu functionalitate la Course 1, 2, ...
#import streamlit as st
#import base64
#from pathlib import Path

#def render_dialog(pdf_file):
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
#def pdf_viewer(pdf_file):
#    with open(pdf_file, "rb") as f:
#        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
#    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700px"></iframe>'
#    st.markdown(pdf_display, unsafe_allow_html=True)


# Mock Query Response
#def respond_to_query(query, dialog_type):
#    return f"Response to '{query}' in context of '{dialog_type}'."


####################### incercare de functionalitate la Survey:

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import base64


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
                st.success("You have completed the survey! Click 'Submit' to generate the report.")
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



def render_dialog(pdf_file):
    left, right = st.columns([0.6, 0.4])  # Adjust column width to 60% / 40%

    if st.session_state['connected']:
        if st.session_state.get("survey_active", False):
            st.title("Feedback Survey")
            render_survey()
        else:
            # Left Zone: Display PDF or course content
            with left:
                if pdf_file:
                    st.subheader(f"Content for {pdf_file}")
                    try:
                        pdf_viewer(st.session_state["pdf_file"])
                        # pdf_viewer(st.session_state["pdf_file"])
                        # with open(pdf_file, "rb") as pdf:
                        #     pdf_data = pdf.read()
                        #     st.download_button(
                        #         label="Download PDF",
                        #         data=pdf_data,
                        #         file_name=pdf_file.split("/")[-1],
                        #         mime="application/pdf",
                        #     )
                        #     st.markdown(
                        #         f'<iframe src="data:application/pdf;base64,{base64.b64encode(pdf_data).decode()}" '
                        #         f'width="100%" height="700px"></iframe>',
                        #         unsafe_allow_html=True,
                        #     )

                    except FileNotFoundError:
                        st.error("PDF file not found. Please check the file path.")
                else:
                    st.info("No course selected. Please select a course from the sidebar.")

            # Right Zone: Chat Interface
            with right:
                st.subheader("Chat Interface")
                dialog_type = st.selectbox("Select Dialog Type", ["Learning", "Evaluation"], key="dialog_type")
                user_input = st.text_input("Ask a question or start the dialog:", key="user_input")

                if user_input:
                    response = respond_to_query(user_input, dialog_type)
                    st.write(response)

# # Mock Query Response
# def respond_to_query(query, dialog_type):
#     return f"Response to '{query}' in context of '{dialog_type}'."
