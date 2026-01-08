from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from services.chunker import split_text
from config import VECTOR_DB_PATH
import os

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def store_chunks(text: str):
    embeddings = get_embeddings()
    db = FAISS.from_texts(chunks, embeddings)
    db.save_local(VECTOR_DB_PATH)

def query_chunks(query: str, k: int = 4):
    if not os.path.exists(VECTOR_DB_PATH):
        return []

    db = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return db.similarity_search(query, k=k)
