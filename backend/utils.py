import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO)

def format_text(text):
    return text.strip().capitalize()
