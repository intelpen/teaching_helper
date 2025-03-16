from dotenv import load_dotenv  # nopep8
import os  # nopep8
import sys  # nopep8
sys.path.insert(0, '.')  # nopep8
sys.path.insert(0, '..')  # nopep8

from backend.helpers.highlighting import PDFHighlighter
from backend.llms.vector_store import VectorStoreWrapper
from backend.llms.llm_gemini import LLMGemini
from backend.llms.rag_protocol import RagProtocol
from backend.llms.llm_protocol import LLMProtocol
import json
from backend.llms.rag_chroma import RagChroma


class LLMRag(LLMProtocol, RagProtocol):
    def __init__(self, config=None, backend=None):
        load_dotenv()
        if config is None:
            config = json.load(
                open('backend/config.json', 'rt'))['LLMGeminiRag']
        self.config = config
        print(f'config {config} \n -------------------------------')

        self.name = 'LLMRag'
        if backend is None:
            # intitialize a default LLM
            self.backend = LLMGemini(config)  # TODO: Change LLMDefault(config)
        else:
            self.backend = backend

        # initialize chroma if needded
        # self.config = config[self.backend.name]
        self.rag = RagChroma()

    def process_request(self, message):
        # system_prompt = self.config['system_prompt']
        # Augment the prompt
        aug_prompt, context, sources = self.rag.augment_prompt(message)
        response = self.backend.process_request(aug_prompt)
        response['context'] = context
        response['sources'] = sources
        print(f"text: {response['text']}")
        print(f"context: {response['context']}")
        return response

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
