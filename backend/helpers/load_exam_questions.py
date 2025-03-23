import json
import sqlite3
import os


def create_database():
    """Create SQLite database and tables for exam questions"""
    # Connect to SQLite database (will create it if it doesn't exist)
    conn = sqlite3.connect('exam_questions.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        exam_id INTEGER,
        question_number INTEGER,
        question_text TEXT,
        FOREIGN KEY (exam_id) REFERENCES exams (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY,
        question_id INTEGER,
        answer_text TEXT,
        is_correct BOOLEAN,
        explanation TEXT,
        FOREIGN KEY (question_id) REFERENCES questions (id)
    )
    ''')

    conn.commit()
    return conn


def load_json_data(file_path):
    """Load JSON data from the specified file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{file_path}'.")
        return None


def insert_data(conn, data):
    """Insert data into the database"""
    cursor = conn.cursor()

    # Insert exam information
    cursor.execute(
        "INSERT INTO exams (title, description) VALUES (?, ?)",
        ('SQL Exam', 'SQL Free Form Questions')
    )
    exam_id = cursor.lastrowid

    # If data is a list, treat each item as a question
    questions = data if isinstance(data, list) else [data]

    # Insert questions and answers
    for i, question_data in enumerate(questions, 1):
        # Extract question text
        question_text = ""
        if isinstance(question_data, dict):
            question_text = question_data.get('question', '')
            if not question_text and 'text' in question_data:
                question_text = question_data.get('text', '')
        else:
            # If question is a string or other type
            question_text = str(question_data)

        cursor.execute(
            "INSERT INTO questions (exam_id, question_number, question_text) VALUES (?, ?, ?)",
            (exam_id, i, question_text)
        )
        question_id = cursor.lastrowid

        # Handle answers if question_data is a dictionary
        if isinstance(question_data, dict):
            # Try different possible answer fields
            answers = question_data.get('answers', [])
            correct_answer = question_data.get('correct_answer', '')
            explanation = question_data.get('explanation', '')

            # Process answers if they exist
            if answers:
                if isinstance(answers, list):
                    for answer in answers:
                        if isinstance(answer, dict):
                            # If answers are objects with properties
                            answer_text = answer.get('text', '')
                            is_correct = answer.get('correct', False)
                            ans_explanation = answer.get('explanation', '')
                        else:
                            # If answers are just strings
                            answer_text = str(answer)
                            is_correct = False  # Default
                            ans_explanation = ''

                        cursor.execute(
                            "INSERT INTO answers (question_id, answer_text, is_correct, explanation) VALUES (?, ?, ?, ?)",
                            (question_id, answer_text, is_correct, ans_explanation)
                        )
                elif isinstance(answers, dict):
                    # If answers are stored as a dict
                    for key, value in answers.items():
                        cursor.execute(
                            "INSERT INTO answers (question_id, answer_text, is_correct, explanation) VALUES (?, ?, ?, ?)",
                            (question_id, str(value), key == 'correct', explanation)
                        )

            # Add correct answer if it exists and no answers were added
            if correct_answer:
                cursor.execute(
                    "INSERT INTO answers (question_id, answer_text, is_correct, explanation) VALUES (?, ?, ?, ?)",
                    (question_id, str(correct_answer), True, explanation)
                )

    conn.commit()


def get_question_by_id(question_id):
    """
    Retrieve a question by its ID and return it in JSON format
    similar to the original structure
    """
    conn = sqlite3.connect('exam_questions.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()

    # Get question data
    cursor.execute("""
        SELECT q.id, q.question_text, e.title, e.description
        FROM questions q
        JOIN exams e ON q.exam_id = e.id
        WHERE q.id = ?
    """, (question_id,))

    question_row = cursor.fetchone()

    if not question_row:
        conn.close()
        return {"error": f"Question with ID {question_id} not found"}

    # Get answers for this question
    cursor.execute("""
        SELECT answer_text, is_correct, explanation
        FROM answers
        WHERE question_id = ?
    """, (question_id,))

    answers_rows = cursor.fetchall()

    # Format the question data in JSON
    question_data = {
        "id": question_row["id"],
        "question": question_row["question_text"],
        "answers": []
    }

    # Add answers
    correct_answer = None
    explanation = None

    for answer in answers_rows:
        answer_obj = {
            "text": answer["answer_text"],
            "correct": bool(answer["is_correct"])
        }

        if answer["explanation"]:
            answer_obj["explanation"] = answer["explanation"]

        question_data["answers"].append(answer_obj)

        # Keep track of correct answer and explanation
        if answer["is_correct"]:
            correct_answer = answer["answer_text"]
            if answer["explanation"]:
                explanation = answer["explanation"]

    # Add correct_answer field if we found one
    if correct_answer:
        question_data["correct_answer"] = correct_answer

    # Add explanation if we found one
    if explanation:
        question_data["explanation"] = explanation

    conn.close()
    return question_data


def get_all_questions():
    """
    Retrieve all questions and return them in JSON format
    """
    conn = sqlite3.connect('exam_questions.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all question IDs
    cursor.execute("SELECT id FROM questions ORDER BY question_number")
    question_ids = [row["id"] for row in cursor.fetchall()]

    conn.close()

    # Get detailed data for each question
    questions = [get_question_by_id(q_id) for q_id in question_ids]

    return questions


def main():
    """Main function to initialize database and load data"""
    file_path = 'data/evaluator/examen_sql_free_form_3.json'

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    # Create database and tables
    conn = create_database()

    # Load JSON data
    data = load_json_data(file_path)
    if data:
        # Insert data into database
        insert_data(conn, data)
        print(
            f"Successfully loaded data from '{file_path}' into the database.")

    print(get_all_questions())
    # Close connection
    conn.close()

    # Example of retrieving a question (uncomment to test)
    # question = get_question_by_id(1)
    # print(json.dumps(question, indent=2))

    # Example of retrieving all questions (uncomment to test)
    # all_questions = get_all_questions()
    # print(json.dumps(all_questions, indent=2))


if __name__ == "__main__":
    main()
