import ollama
from config import MODEL

def get_response(messages):
    response = ollama.chat(
        model=MODEL,
        messages=messages,
    )
    return response["message"]["content"]


