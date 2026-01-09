from pinecone import Pinecone
from services.embeddings import embed_texts
import os, uuid

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))


def store_chunks(chunks: list[str]):
    # 1️⃣ Remove empty chunks (very important)
    chunks = [c for c in chunks if c and c.strip()]

    if not chunks:
        return

    # 2️⃣ Embed
    vectors = embed_texts(chunks)

    if not vectors:
        raise ValueError("No embeddings returned")

    # 3️⃣ Prevent mismatch crashes
    min_len = min(len(chunks), len(vectors))

    if len(chunks) != len(vectors):
        print(
            f"[WARN] Chunk/embedding mismatch: "
            f"{len(chunks)} chunks vs {len(vectors)} vectors"
        )

    # 4️⃣ Ensure Pinecone-safe format
    items = []
    for i in range(min_len):
        items.append(
            (
                str(uuid.uuid4()),
                vectors[i].tolist(),   # 🔥 CRITICAL
                {"text": chunks[i]}
            )
        )

    # 5️⃣ Upsert once (efficient)
    index.upsert(items)


def query_chunks(query: str, k: int = 4):
    q_emb = embed_texts([query])[0].tolist()  # already correct
    res = index.query(
        vector=q_emb,
        top_k=k,
        include_metadata=True
    )

    return [
        match["metadata"]["text"]
        for match in res.get("matches", [])
    ]
