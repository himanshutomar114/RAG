from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from collections import defaultdict
import time

from services.document_loader import load_document
from services.url_loader import load_from_url
from services.chunker import split_text
from services.vector_store import store_chunks, query_chunks
from services.rag_chain import generate_answer

load_dotenv()

app = FastAPI()

# ---------------- RATE LIMITER ---------------- #

class TokenRateLimiter:
    def __init__(self):
        self.token_requests = defaultdict(list)

    def is_allowed(self, token: str, limit: int, window_seconds: int = 60) -> bool:
        now = time.time()
        cutoff = now - window_seconds

        self.token_requests[token] = [
            t for t in self.token_requests[token] if t > cutoff
        ]

        if len(self.token_requests[token]) < limit:
            self.token_requests[token].append(now)
            return True
        return False

limiter = TokenRateLimiter()

# ---------------- SCHEMAS ---------------- #

class ChatRequest(BaseModel):
    query: str

class URLRequest(BaseModel):
    url: str

# ---------------- ENDPOINTS ---------------- #

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_token: str = Header(...)
):
    if not limiter.is_allowed(x_token, limit=5):
        raise HTTPException(429, "Rate limit exceeded (5/min)")

    text = load_document(file)
    chunks = split_text(text)

    store_chunks(chunks)

    return {
        "status": "success",
        "chunks_indexed": len(chunks)
    }


@app.post("/ingest-url")
async def ingest_url(
    data: URLRequest,
    x_token: str = Header(...)
):
    if not limiter.is_allowed(x_token, limit=10):
        raise HTTPException(429, "Rate limit exceeded (10/min)")

    text = load_from_url(data.url)
    chunks = split_text(text)

    store_chunks(chunks)

    return {
        "status": "success",
        "chunks_indexed": len(chunks),
        "url": data.url
    }


@app.post("/chat")
async def chat(
    data: ChatRequest,
    x_token: str = Header(...)
):
    if not limiter.is_allowed(x_token, limit=30):
        raise HTTPException(429, "Rate limit exceeded (30/min)")

    docs = query_chunks(data.query)
    answer = generate_answer(data.query, docs)

    return {
        "answer": answer
    }
