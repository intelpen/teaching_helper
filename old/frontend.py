import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000"

# Sidebar
st.sidebar.title("Autentificare")

if 'user_id' not in st.session_state:
    choice = st.sidebar.radio("Alege o acțiune:", ["Logare", "Înregistrare"])

    if choice == "Logare":
        username = st.sidebar.text_input("Nume utilizator")
        password = st.sidebar.text_input("Parolă", type="password")
        if st.sidebar.button("Logare"):
            response = requests.post(
                f"{API_URL}/login", json={'username': username, 'password': password}).json()
            if 'user_id' in response:
                st.session_state['user_id'] = response['user_id']
                st.success("Logare reușită!")
            else:
                st.error(response.get('error', 'Eroare necunoscută'))

    elif choice == "Înregistrare":
        username = st.sidebar.text_input("Nume utilizator")
        password = st.sidebar.text_input("Parolă", type="password")
        if st.sidebar.button("Înregistrare"):
            response = requests.post(
                f"{API_URL}/register", json={'username': username, 'password': password}).json()
            if 'status' in response:
                st.success("Utilizator înregistrat!")
            else:
                st.error(response.get('error', 'Eroare necunoscută'))
else:
    st.sidebar.write(
        f"Bine ai venit, Utilizator {st.session_state['user_id']}!")

    # Alege capitol
    chapters = requests.get(f"{API_URL}/chapters").json()
    chapter_titles = [chapter[1] for chapter in chapters]
    selected_chapter = st.sidebar.selectbox(
        "Selectează un capitol", chapter_titles)

    if selected_chapter:
        chapter_id = chapters[chapter_titles.index(selected_chapter)][0]
        questions = requests.get(f"{API_URL}/questions/{chapter_id}").json()

        for question in questions:
            st.subheader(question[3])
            if question[2] == "text":
                user_answer = st.text_input(f"Răspuns pentru {question[3]}")
            elif question[2] == "code":
                user_answer = st.text_area(
                    f"Introdu codul pentru {question[3]}")
            elif question[2] == "true_false":
                user_answer = st.radio(
                    f"Răspuns pentru {question[3]}", ["True", "False"])

            if st.button(f"Verifică răspunsul pentru {question[3]}"):
                response = requests.post(f"{API_URL}/evaluate", json={
                    'question_id': question[0],
                    'user_answer': user_answer
                }).json()
                if response['correct']:
                    st.success("Răspuns corect!")
                else:
                    st.error("Răspuns greșit.")

                if st.button(f"Salvează răspunsul"):
                    requests.post(f"{API_URL}/save_response", json={
                        'user_id': st.session_state['user_id'],
                        'question_id': question[0],
                        'is_correct': response['correct']
                    })

    if st.sidebar.button("Vezi analiza răspunsurilor"):
        analytics = requests.get(
            f"{API_URL}/analytics/{st.session_state['user_id']}").json()
        st.sidebar.write(f"Încercări totale: {analytics['total_attempts']}")
        st.sidebar.write(
            f"Răspunsuri corecte: {analytics['correct_attempts']}")
        st.sidebar.write(f"Acuratețe: {analytics['accuracy']:.2f}%")
