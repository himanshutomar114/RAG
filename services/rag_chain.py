import requests
from services.vector_store import query_chunks
from config import HUGGINGFACEHUB_API_TOKEN

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}

def generate_answer(question: str):
    docs = query_chunks(question)
    context = "\n".join([doc.page_content for doc in docs])

    payload = {
        "inputs": f"Context: {context}\nQuestion: {question}\nAnswer:"
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()[0]["generated_text"]
