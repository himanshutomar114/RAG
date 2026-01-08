from huggingface_hub import InferenceClient
import os

client = InferenceClient(
    model="sentence-transformers/all-MiniLM-L6-v2",
    token=os.getenv("HF_API_TOKEN")
)

def embed_texts(texts: list[str]) -> list[list[float]]:
    return client.feature_extraction(texts)
