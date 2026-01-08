# services/embeddings.py
import requests
import os

HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

headers = {
    "Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"
}

def embed_texts(texts: list[str]) -> list[list[float]]:
    response = requests.post(
        HF_API_URL,
        headers=headers,
        json={"inputs": texts}
    )
    response.raise_for_status()
    return response.json()
