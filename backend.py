from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database setup


def init_db():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    # Chapters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Chapters (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT
        )
    ''')

    # Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Questions (
            id INTEGER PRIMARY KEY,
            chapter_id INTEGER,
            type TEXT,
            content TEXT,
            correct_answer TEXT,
            FOREIGN KEY(chapter_id) REFERENCES Chapters(id)
        )
    ''')

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    ''')

    # Responses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Responses (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            question_id INTEGER,
            is_correct BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES Users(id),
            FOREIGN KEY(question_id) REFERENCES Questions(id)
        )
    ''')

    conn.commit()
    conn.close()


@app.route('/chapters', methods=['GET'])
def get_chapters():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Chapters")
    chapters = cursor.fetchall()
    conn.close()
    return jsonify(chapters)


@app.route('/questions/<int:chapter_id>', methods=['GET'])
def get_questions(chapter_id):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Questions WHERE chapter_id=?", (chapter_id,))
    questions = cursor.fetchall()
    conn.close()
    return jsonify(questions)


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    password_hash = generate_password_hash(password)

    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return jsonify({'status': 'User registered successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        conn.close()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, password_hash FROM Users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        return jsonify({'status': 'Login successful', 'user_id': user[0]})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/save_response', methods=['POST'])
def save_response():
    data = request.json
    user_id = data['user_id']
    question_id = data['question_id']
    is_correct = data['is_correct']

    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Responses (user_id, question_id, is_correct) VALUES (?, ?, ?)",
                   (user_id, question_id, is_correct))
    conn.commit()
    conn.close()
    return jsonify({'status': 'Response logged'})


@app.route('/analytics/<int:user_id>', methods=['GET'])
def analytics(user_id):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM Responses WHERE user_id=?", (user_id,))
    total_attempts = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM Responses WHERE user_id=? AND is_correct=1", (user_id,))
    correct_attempts = cursor.fetchone()[0]

    conn.close()

    accuracy = (correct_attempts / total_attempts *
                100) if total_attempts > 0 else 0
    return jsonify({
        'total_attempts': total_attempts,
        'correct_attempts': correct_attempts,
        'accuracy': accuracy
    })


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
