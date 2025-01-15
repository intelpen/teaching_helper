"""TODO: Move the rest from carrie_rag here 
"""
import os
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.docstore.document import Document
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class VectorStoreWrapper:
    """I include the chunker here, but it can be further splitted to a separate chunker
    """

    def __init__(self, config):
        self.embedding_function = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-mpnet-base-v2')  # os.environ.get('EMBEDDING_MODEL_PATH'))
        self.pdfs_dir = 'data/pdfs/'
        self.loader = DirectoryLoader(self.pdfs_dir, glob="**/*.pdf", show_progress=True, use_multithreading=True,
                                      loader_cls=PyPDFLoader)

        self.collection_name = "collection-main"
        self.db_persist_directory = "data/db"

        if os.path.exists(self.db_persist_directory):
            self.chromadb_instance = Chroma(persist_directory=self.db_persist_directory,
                                            collection_name=self.collection_name,
                                            embedding_function=self.embedding_function)
        else:
            print("No embeddings db directory found!")
            print("Loading documents..")
            self.documents = self.load_default_docs_and_split_into_chunks()
            print(self.documents)
            print("Generating embeddings..")
            self.generate_default_embeddings_database(documents=self.documents)

            print("Embeddings generated!")

    def split_docs_recursive_character(self, documents: list[Document]):
        # Splitting docs (text) into chunks with a sentence limit (todo: add sentence limit in config file)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000, chunk_overlap=300)
        transformed_documents = text_splitter.transform_documents(documents)
        splitted_documents = []
        for i in range(len(transformed_documents)):
            tr_id = transformed_documents[i].id
            tr_chunk = transformed_documents[i].page_content
            tr_metadata = transformed_documents[i].metadata
            splitted_documents.append(
                Document(
                    id=tr_id,
                    metadata=tr_metadata,
                    page_content=tr_chunk
                )
            )
        return splitted_documents

    def load_default_docs_and_split_into_chunks(self):
        print("\nloading documents..")
        print("Current directory:", os.getcwd())
        # Load internal documents but do not split them yet
        documents = self.loader.load()
        # Split documents with rec ch technique
        transformed_documents = self.split_docs_recursive_character(documents)
        return transformed_documents

    def load_default_docs(self):
        # TODO: this might be redudant because of load_default_docs_and_split_into_chunks fucn
        # TODO: make a better check for existing documents
        if os.path.exists(self.pdfs_dir):
            print(
                "Embeddings for default documents already existent, skipping file upload..")
            return False
        else:
            print("\nloading documents..")
            # Load internal documents
            # TODO: add document spliter choice (RecursiveCharacterTextSplitter,separators,MarkdownHeaderTextSplitter)
            documents = self.loader.load_and_split()
            return documents

    def generate_default_embeddings_database(self, documents: list[Document]):
        print("\nNo embeddings folder found, generating embeddings..")
        self.chromadb_instance = Chroma.from_documents(documents=documents,
                                                       embedding=self.get_embedding_function(),
                                                       collection_name=self.collection_name,
                                                       persist_directory=self.db_persist_directory,
                                                       collection_metadata={
                                                           "hnsw:space": "cosine"}
                                                       )
        print("\nGenerating embeddings.. Done")

        print("\nPersisting the vector store..")
        self.chromadb_instance.persist()
        print("\nPersisting the vector store.. Done")

        return True

    def load_new_docs(self, documents):
        # TODO
        return False

    def update_embeddings_database(self, documents):
        # TODO
        return False

    def get_question_context(self, original_user_prompt):
        # embed the user prompt
        embedding_function = self.get_embedding_function()
        query_embedding = embedding_function.embed_query(original_user_prompt)
        # get the most relevant document for the user prompt
        # k will be a praram in testing. What is the advantage of byvector #use metadata like chapter title ?
        retrieved_docs = self.chromadb_instance.similarity_search_by_vector(
            query_embedding, k=2)
        return retrieved_docs

    def get_embedding_function(self):
        return self.embedding_function
