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


class LLMRagEvaluator(LLMRag):
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

    def evaluate_answer(self, question_id, answer_text):
        # avem legatura la self.df
        # question_id, question_text, question_type {free-form | multi-choice}, reference_answer, relevant_sections_list
        question = self.db.get_question(question_id)
        prompt_template = """
        You are an exam evaluator. 
        You will evaluate the answer "STUDENT_ANSWER" to the questin "QUESTION" with respect to the following topics "TOPICS".
        Use "REFERENCE_ANSWER" as reference to guide your evaluation.
        Evaluate which topics has been correctly answered.

        Provide an answer in json format with the following structure:
        " {'general_feedback': 'your general feedback to the answer, including suggestion for the student on which sections_id he needs to reread to improve his answer', 
            {'topic':'Topic_1'
             'evaluation': 'PASS/ FAIL',
             'sections_used' : ' [list of sections id] used in the student anser to adress this topic, or None'
             'answer_text_quote': 'quote the text from the question who answers this token'
             'justification':'the justification for passing/failing the topic'
            }
            {'topic':'Topic_2'... }
            ...
             }
        ---------
        STUDENT_ANSWEER %1
        ---------
        QUESTION %2
        -----------
        REFERENCE_ANSWER %3
        -----------
        TOPICS %4
        ----------
        REFERENCE_SECTIONS_LIST %
        ---------
        """
        prompt_evaluator = prompt_template.format(
            student_answer, question, refefrence_answer, topics, reference_sections_list)
        answer_json = self.llm.process_request_json(prompt_evaluator)

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
