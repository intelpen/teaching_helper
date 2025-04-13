
import sys
sys.path.insert(0, '.')  # nopep8
sys.path.insert(0, '..')  # nopep8
import json
from backend.llms.rag_protocol import RagProtocol
from backend.llms.vector_store import VectorStoreWrapper


class RagChroma(RagProtocol):

    def __init__(self, config=None):
        if config is None:
            config = json.load(
                open('backend/config.json', 'rt'))['LLMGeminiRag']
        self.config = config
        self.name = 'RagChroma'
        self.vector_store = VectorStoreWrapper(config)
        self.embedding_function = self.vector_store.embedding_function

    def augment_prompt(self, original_user_prompt):
        if self.config['chunker_name'] == "pages":
            return self.augment_prompt_with_pages(original_user_prompt)
        elif self.config['chunker_name'] == "chunks":
            return self.augment_prompt_with_chunks(original_user_prompt)


    def retrieve_docs(self, message):
        raise NotImplementedError

    def log(self):
        raise NotImplementedError


if __name__ == "__main__":
    """rag with gemini backend
    """
    backend_llm = LLMGemini()
    llmrag = LLMRag(backend=backend_llm)
    print(llmrag.process_request("why is six afraid of seven").text)
