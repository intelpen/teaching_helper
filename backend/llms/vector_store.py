import os
from collections import defaultdict
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.docstore.document import Document
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


class VectorStoreWrapper:
    """
    This wrapper loads PDFs from a directory, cleans the text, and then either
    splits the text into chunks (potentially spanning multiple pages from the same PDF)
    or treats each page as a separate document.
    """

    def __init__(self, config):
        self.embedding_function = HuggingFaceEmbeddings(
            model_name='sentence-transformers/distiluse-base-multilingual-cased-v2'
        )
        self.pdfs_dir = 'data/pdfs/'
        self.loader = DirectoryLoader(
            self.pdfs_dir,
            glob="**/*.pdf",
            show_progress=True,
            use_multithreading=True,
            loader_cls=PyPDFLoader
        )

        self.collection_name = "collection-main"
        self.db_persist_directory = "data/db"

        if os.path.exists(self.db_persist_directory):
            self.chromadb_instance = Chroma(
                persist_directory=self.db_persist_directory,
                collection_name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print('Folder exists, no new chroma db')
        else:
            print("No embeddings db directory found!")
            print("Loading documents..")
            if config["chunker_name"] == "chunks":
                print('Splitting by chunks')
                self.documents = self.load_default_docs_and_split_into_chunks()
                print(f'Documents len {len(self.documents)} ')
            else:
                print('Splitting by pages')
                self.documents = self.load_default_docs_and_split_into_pages()
                print(f'Documents len {len(self.documents)} ')

            print(f"Documents loaded in DB {self.documents}")
            print("Generating embeddings..")
            self.generate_default_embeddings_database(documents=self.documents)
            print("Embeddings generated!")

    def remove_standard_text(self, text: str) -> str:
        """
        Remove known unwanted text fragments from the given text.
        """
        text_to_remove = [
            'Baze de date\nAdrian \nRunceanu\nLimbajul SQL\nUCB: Universitatea Constantin Brâncuși din Târgu-Jiu\nAutomatică și Informatică Aplicată',
            'copyright@www.adrian.runceanu.ro\n',
            'Curs - Baze de date\n',
            'Curs - Baze de date',
        ]
        for phrase in text_to_remove:
            text = text.replace(phrase, "")
        return text

    def split_docs_recursive_character(self, documents: list[Document]):
        """
        Group pages by PDF file (based on the 'source' metadata) so that all pages
        from the same PDF are combined into one document. Before combining, the text is
        cleaned by removing standard unwanted text. Then, use the RecursiveCharacterTextSplitter
        to split the combined text into chunks (each chunk coming from a single PDF).
        """
        # Group documents (pages) by PDF source.
        docs_by_source = defaultdict(list)
        for doc in documents:
            # Assume that each document's metadata contains a 'source' field with the PDF file path.
            source = doc.metadata.get("source", "unknown")
            docs_by_source[source].append(doc)

        # Combine pages from the same PDF.
        combined_docs = []
        for source, docs in docs_by_source.items():
            # Optionally sort pages if a page number is available in metadata.
            docs_sorted = sorted(docs, key=lambda x: x.metadata.get("page", 0))
            # Remove standard text from each page and combine using double newlines.
            combined_text = "\n\n".join(
                [self.remove_standard_text(d.page_content) for d in docs_sorted])
            # Copy metadata from the first page and update with PDF-level info.
            new_metadata = docs_sorted[0].metadata.copy(
            ) if docs_sorted else {}
            new_metadata["source"] = source
            new_metadata["num_pages"] = len(docs_sorted)
            combined_docs.append(
                Document(id=source, metadata=new_metadata, page_content=combined_text))

        # Now split the combined documents using the RecursiveCharacterTextSplitter.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000, chunk_overlap=300)
        transformed_documents = text_splitter.transform_documents(
            combined_docs)
        return transformed_documents

    def split_docs_pages(self, documents: list[Document]):
        """
        Return the documents as they are (i.e., one document per page) with standard text removed.
        """
        splitted_documents = []
        for doc in documents:
            cleaned_text = self.remove_standard_text(doc.page_content)
            splitted_documents.append(
                Document(
                    id=doc.id,
                    metadata=doc.metadata,
                    page_content=cleaned_text
                )
            )
        return splitted_documents

    def load_default_docs_and_split_into_chunks(self):
        print("\nLoading documents...")
        print("Current directory:", os.getcwd())
        # Load documents (pages) using the loader.
        documents = self.loader.load()
        # Group pages by PDF and split into chunks.
        transformed_documents = self.split_docs_recursive_character(documents)
        return transformed_documents

    def load_default_docs_and_split_into_pages(self):
        print("\nLoading documents...")
        print("Current directory:", os.getcwd())
        # Load documents (pages) using the loader.
        documents = self.loader.load()
        # Return one document per page after cleaning the text.
        transformed_documents = self.split_docs_pages(documents)
        return transformed_documents

    def load_default_docs(self):
        # TODO: this might be redundant because of load_default_docs_and_split_into_chunks func.
        # TODO: make a better check for existing documents.
        if os.path.exists(self.pdfs_dir):
            print(
                "Embeddings for default documents already exist, skipping file upload..")
            return False
        else:
            print("\nLoading documents...")
            # Load internal documents and split them.
            documents = self.loader.load_and_split()
            return documents

    def generate_default_embeddings_database(self, documents: list[Document]):
        print("\nNo embeddings folder found, generating embeddings..")
        self.chromadb_instance = Chroma.from_documents(
            documents=documents,
            embedding=self.get_embedding_function(),
            collection_name=self.collection_name,
            persist_directory=self.db_persist_directory,
            collection_metadata={"hnsw:space": "cosine"}
        )
        print("\nGenerating embeddings.. Done")

        print("\nPersisting the vector store.. automatically ")
        try:
            self.chromadb_instance.persist()
        except Exception as e:
            print(
                'Persist cannot be called because in this version it is done automatically')
        print("\nPersisting the vector store.. Done")
        return True

    def load_new_docs(self, documents):
        # TODO: implement document loading for new documents.
        return False

    def update_embeddings_database(self, documents):
        # TODO: implement database updates.
        return False

    def get_question_context(self, original_user_prompt):
        # Embed the user prompt.
        query_embedding = self.embedding_function.embed_query(
            original_user_prompt)
        # Retrieve the most relevant documents (k can be adjusted as needed).
        retrieved_docs = self.chromadb_instance.similarity_search_by_vector(
            query_embedding, k=2)
        return retrieved_docs

    def get_embedding_function(self):
        return self.embedding_function
