from pinecone import Pinecone
from services.embeddings import embed_texts
import os, uuid

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

UPSERT_BATCH_SIZE = 50   # SAFE for 384-dim embeddings

def store_chunks(chunks: list[str]):
    chunks = [c for c in chunks if c and c.strip()]
    if not chunks:
        return

    vectors = embed_texts(chunks)
    if vectors is None or len(vectors) == 0:
        raise ValueError("No embeddings returned")

    min_len = min(len(chunks), len(vectors))

    items = [
        (
            str(uuid.uuid4()),
            vectors[i].tolist(),
            {"text": chunks[i]}
        )
        for i in range(min_len)
    ]

    # 🔥 BATCHED UPSERT (THIS FIXES 2MB ERROR)
    for i in range(0, len(items), UPSERT_BATCH_SIZE):
        batch = items[i:i + UPSERT_BATCH_SIZE]
        index.upsert(batch)
