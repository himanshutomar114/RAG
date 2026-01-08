from pinecone import Pinecone
from services.embeddings import embed_texts
import os, uuid

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

def store_chunks(chunks: list[str]):
    vectors = embed_texts(chunks)
    items = [
        (str(uuid.uuid4()), vectors[i], {"text": chunks[i]})
        for i in range(len(chunks))
    ]
    index.upsert(items)

def query_chunks(query: str, k=4):
    q_emb = embed_texts([query])[0].tolist()
    res = index.query(vector=q_emb, top_k=k, include_metadata=True)
    return [m["metadata"]["text"] for m in res["matches"]]
