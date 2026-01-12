from pinecone import Pinecone
from services.embeddings import embed_texts
import os, uuid
from pinecone import PineconeException

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

MAX_CHUNKS = 100
UPSERT_BATCH_SIZE = 50


# =========================
# STORE (PER CHAT)
# =========================
def store_chunks(chunks: list[str], namespace: str):
    # 1️⃣ Remove empty chunks
    chunks = [c for c in chunks if c and c.strip()]
    if not chunks:
        return

    # 2️⃣ Hard limit (memory safety)
    chunks = chunks[:MAX_CHUNKS]

    # 3️⃣ Embed
    vectors = embed_texts(chunks)
    if not vectors:
        raise ValueError("No embeddings returned")

    # 4️⃣ Prevent mismatch
    min_len = min(len(chunks), len(vectors))

    # 5️⃣ Prepare items
    items = [
        (
            str(uuid.uuid4()),
            vectors[i].tolist(),
            {
                "text": chunks[i],
                "namespace": namespace  # optional debug metadata
            }
        )
        for i in range(min_len)
    ]

    # 6️⃣ Batched upsert INTO NAMESPACE
    for i in range(0, len(items), UPSERT_BATCH_SIZE):
        batch = items[i:i + UPSERT_BATCH_SIZE]
        index.upsert(batch, namespace=namespace)


# =========================
# QUERY (PER CHAT)
# =========================
def query_chunks(query: str, namespace: str, k: int = 4):
    q_emb = embed_texts([query])[0].tolist()

    res = index.query(
        vector=q_emb,
        top_k=k,
        namespace=namespace,
        include_metadata=True
    )

    return [
        match["metadata"]["text"]
        for match in res.get("matches", [])
    ]


# =========================
# DELETE CHAT MEMORY 🔥
# =========================
def delete_namespace(namespace: str):
    try:
        index.delete(delete_all=True, namespace=namespace)
    except PineconeException:
        # Namespace does not exist → nothing to delete
        pass