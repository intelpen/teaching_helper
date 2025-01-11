import os


class MarkdownUtils:
    @staticmethod
    def make_relative_path_linkable(relative_path, link_text):
        absolute_path = os.path.abspath(relative_path)
        download_link = f"[{link_text}]({absolute_path})"
        return download_link
