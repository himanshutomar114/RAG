from pinecone import Pinecone
from services.embeddings import embed_texts
import os, uuid

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

UPSERT_BATCH_SIZE = 50  # 🔒 Safe under Pinecone 2MB limit


def store_chunks(chunks: list[str]):
    # 1️⃣ Remove empty chunks
    chunks = [c for c in chunks if c and c.strip()]
    if not chunks:
        return

    # 2️⃣ Embed
    vectors = embed_texts(chunks)
    if vectors is None or len(vectors) == 0:
        raise ValueError("No embeddings returned")

    # 3️⃣ Prevent mismatch crashes
    min_len = min(len(chunks), len(vectors))
    if len(chunks) != len(vectors):
        print(
            f"[WARN] Chunk/embedding mismatch: "
            f"{len(chunks)} chunks vs {len(vectors)} vectors"
        )

    # 4️⃣ Prepare Pinecone-safe items
    items = [
        (
            str(uuid.uuid4()),
            vectors[i].tolist(),   # 🔥 REQUIRED
            {"text": chunks[i]}
        )
        for i in range(min_len)
    ]

    # 5️⃣ 🔥 BATCHED UPSERT (CRITICAL FIX)
    for i in range(0, len(items), UPSERT_BATCH_SIZE):
        batch = items[i:i + UPSERT_BATCH_SIZE]
        index.upsert(batch)


def query_chunks(query: str, k: int = 4):
    q_emb = embed_texts([query])[0].tolist()

    res = index.query(
        vector=q_emb,
        top_k=k,
        include_metadata=True
    )

    return [
        match["metadata"]["text"]
        for match in res.get("matches", [])
    ]
