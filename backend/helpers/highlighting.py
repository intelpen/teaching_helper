import pymupdf
from langchain_community.docstore.document import Document


class PDFHighlighter:
    @staticmethod
    def highlight_text_from_file(original_file_path: str, pages_no_with_chunks: list[
            tuple[int, str]]):
        """
        Method that gets a file and a (page, chunk) tuple and returns a new file with the text highlighted

        :param original_file_path: The path of the original file to copy and highlight the relevant text
        :param pages_no_with_chunks: List of tuples of (page number, relevant chunk context)
        :return: A new path of te file with the text highlighted where is the relevant content
        """
        original_doc = pymupdf.open(original_file_path)

        for current_page_no_with_chunk in pages_no_with_chunks:
            # Unzip the tuple of (page number, relevant chunk context)
            page_no = current_page_no_with_chunk[0]
            chunk_to_highlight = current_page_no_with_chunk[1]

            # Load the page in which we highlight the chunk
            current_page = original_doc[page_no]
            # Search for the current chunk
            # For the return type Rect checkout: https://pymupdf.readthedocs.io/en/latest/rect.html#rect
            rects = current_page.search_for(chunk_to_highlight)

            # Mark occurrences (all the chunks found in one go, but in general should be only one found)
            current_page.add_highlight_annot(rects)

        highlighted_file_path = original_file_path + "_source.pdf"
        original_doc.save(highlighted_file_path)

        return highlighted_file_path
