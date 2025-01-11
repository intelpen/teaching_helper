from helpers.highlighting import PDFHighlighter
from llms.vector_store import VectorStoreWrapper
from llms.llm_gemini import LLMGemini
from llms.rag_protocol import RagProtocol
from llms.llm_protocol import LLMProtocol
import json
import os
import sys

from dotenv import load_dotenv

print(os.getcwd())
sys.path.insert(0, '.')


class LLMRag(LLMProtocol, RagProtocol):
    def __init__(self, config=None, backend=None):
        load_dotenv()
        if config is None:
            config = json.load(open('config.json', 'rt'))['LLMGemini']
        self.config = config

        self.name = 'LLMRag'
        if backend is None:
            # intitialize a default LLM
            self.backend = LLMGemini(config)  # TODO: Change LLMDefault(config)
        else:
            self.backend = backend

        # initialize chroma if needded
        # self.config = config[self.backend.name]
        self.vector_store = VectorStoreWrapper(config)
        self.embedding_function = self.vector_store.embedding_function

    # Augment the prompt
    def augment_prompt_with_chunks(self, original_user_prompt, highlighting=True):
        # Get the most relevant chunks for the user prompt
        retrieved_chunks_with_scores = self.vector_store.chromadb_instance.similarity_search_with_relevance_scores(
            original_user_prompt, k=self.config['top_k'])

        augmented_prompt = ""
        similarity_threshold = self.config['similarity_threshold']
        relevant_content = []
        sources = set()
        chunk_no = 0

        highlight_data = dict()

        for chunk, similarity_score in retrieved_chunks_with_scores:
            chunk_source = chunk.metadata['source']

            source_page_no = chunk.metadata['page']
            chunk_content = chunk.page_content

            # Create or add to the source path a new chunk along with its corresponding page number from where
            # it is taken
            # This dict is used to create a highlighted new document
            highlight_data.setdefault(chunk_source, []).append(
                tuple((source_page_no, chunk_content)))

            chunk_no += 1

            if similarity_score >= similarity_threshold:
                # The chunks are ordered by default by relevance,
                # the first chunk being the most similar with the user's prompt
                # Enumerate all the chunks to give the LLM a structured view of the ordered chunks based on relevance
                relevant_content.append(str(chunk_no) + ". ")
                relevant_content.append(chunk_content)
                # Break each chunk for structure
                relevant_content.append("\n")

                if highlighting:
                    for source_path, pages_no_with_chunks in highlight_data.items():
                        sources.add(PDFHighlighter.highlight_text_from_file(original_file_path=source_path,
                                                                            pages_no_with_chunks=pages_no_with_chunks))
                else:
                    sources.add(os.path.basename(chunk_source))

        # If the score isn't passed just instruct the LLM to respond with a specific answer for this case
        if len(relevant_content) == 0:
            no_context_prompt = self.config['no_internal_source_prompt']
            augmented_prompt += no_context_prompt
            # Return the augmented prompt with the specific answer for no relevant context in sources
            return augmented_prompt, relevant_content, sources

        # If there are sources which are relevant, give the system prompt the rules to answer

        augmented_prompt += self.config['internal_source_rules']

        augmented_prompt += f"""
        ORIGINAL USER PROMPT: {original_user_prompt}
        \n
        CONTEXT FROM INTERNAL SOURCES:\n{" ".join(relevant_content)}
        """
        return augmented_prompt, relevant_content, sources

    def augment_prompt_with_pages(self, original_user_prompt, k=2):
        query_embedding = self.embedding_function.embed_query(
            original_user_prompt)
        retrieved_docs = self.vector_store.chromadb_instance.similarity_search_by_vector(
            query_embedding, k=k)

        # Todo: implement sources like in chunks function
        sources = set()
        sources.add("Unavailable")

        augmented_prompt = f"""
            Answer the User prompt using information from the Context
            USER PROMPT: "{original_user_prompt}"
            \n
            CONTEXT: "{retrieved_docs[0].page_content}""
            \n                                                        
            """
        return augmented_prompt, retrieved_docs, sources

    def augment_prompt(self, original_user_prompt):
        if self.config['chunker_name'] == "pages":
            return self.augment_prompt_with_pages(original_user_prompt, k=2)
        elif self.config['chunker_name'] == "chunks":
            return self.augment_prompt_with_chunks(original_user_prompt)

    def process_request(self, message):
        # system_prompt = self.config['system_prompt']
        # Augment the prompt
        aug_prompt, context, sources = self.augment_prompt(message)
        response = self.backend.process_request(aug_prompt)
        response.context = context
        response.sources = sources
        print(response)
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
