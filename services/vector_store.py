from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

_embeddings = None
_db = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embeddings

def store_chunks(chunks):
    global _db
    embeddings = get_embeddings()
    _db = FAISS.from_texts(chunks, embeddings)

def query_chunks(query, k=4):
    if _db is None:
        return []
    return _db.similarity_search(query, k=k)
