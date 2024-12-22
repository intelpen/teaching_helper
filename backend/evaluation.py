def evaluate_text_answer(correct_answer, user_answer):
    return correct_answer.strip().lower() == user_answer.strip().lower()


def evaluate_code_snippet(correct_code, user_code):
    try:
        exec(correct_code)
        exec(user_code)
        return True, "Code is correct."
    except Exception as e:
        return False, f"Code has errors: {e}"


def calculate_score(responses):
    return sum(1 for r in responses if r) / len(responses) * 100
