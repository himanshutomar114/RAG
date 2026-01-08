from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from services.embeddings import embed_texts
from services.chunker import split_text
from config import VECTOR_DB_PATH
import os

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def store_chunks(text: str):
    chunks = split_text(text)
    embeddings = embed_texts(chunks)
    db = FAISS.from_embeddings(list(zip(chunks, embeddings)))
    db.save_local("/data/faiss")

def query_chunks(query: str, k: int = 4):
    if not os.path.exists(VECTOR_DB_PATH):
        return []

    db = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return db.similarity_search(query, k=k)
