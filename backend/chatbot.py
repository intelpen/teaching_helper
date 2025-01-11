from backend.llms.llm_rag import LLMRag
from backend.llms.llm_gemini import LLMGemini


def start_dialog(dialog_type, user_data):
    if dialog_type == "learning":
        return "Welcome to assisted learning. Let's explore your selected topics!"
    elif dialog_type == "evaluation":
        return "Starting evaluation. Answer the following questions."


def respond_to_query(query, context):
    # Dummy response logic for now
    backend_llm = LLMGemini()
    llmrag = LLMRag(backend=backend_llm)
    response = llmrag.process_request(query)
    return f"{response.text}"
