from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from collections import defaultdict
from fastapi import BackgroundTasks
import time

from services.document_loader import load_document
from services.url_loader import load_from_url
from services.chunker import split_text
from services.vector_store import store_chunks, query_chunks
from services.rag_chain import generate_answer
from services.vector_store import store_chunks, query_chunks, delete_namespace


load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ai-analyzer-omega.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["*"],  # 👈 allows OPTIONS, POST, etc.
    allow_headers=["*"],  # 👈 allows x-token
)


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
    chat_id: str,
    file: UploadFile = File(...),
    x_token: str = Header(...),
    background_tasks: BackgroundTasks = None
):
    
    namespace = f"{x_token}:{chat_id}"

    if not limiter.is_allowed(x_token, limit=5):
        raise HTTPException(429, "Rate limit exceeded (5/min)")

    text = load_document(file)
    chunks = split_text(text)

    background_tasks.add_task(store_chunks, chunks, namespace)

    return {
        "status": "success",
        "chunks_indexed": len(chunks)
    }


@app.post("/ingest-url")
async def ingest_url(chat_id: str, data: URLRequest, x_token: str = Header(...),background_tasks: BackgroundTasks = None):
     
    namespace = f"{x_token}:{chat_id}"

    if not limiter.is_allowed(x_token, limit=10):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        text = load_from_url(data.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    chunks = split_text(text)   # 🔥 MISSING STEP
    background_tasks.add_task(store_chunks, chunks, namespace)
    
    return {
        "message": "URL indexed successfully",
        "chunks_indexed": len(chunks)
    }




@app.post("/chat")
async def chat(chat_id: str, data: ChatRequest, x_token: str = Header(...)):
    
    namespace = f"{x_token}:{chat_id}"

    if not limiter.is_allowed(x_token, limit=30):
        raise HTTPException(429, "Rate limit exceeded (30/min)")

    docs = query_chunks(data.query, namespace, k=4)

    if not docs:
        return {
            "answer": "⚠️ No documents found. Upload a file or ingest a URL first."
        }

    answer = generate_answer(data.query, docs)
    return {"answer": answer}

@app.post("/clear-chat")
async def clear_chat(chat_id: str, x_token: str = Header(...)):
    namespace = f"{x_token}:{chat_id}"

    try:
        delete_namespace(namespace)
    except Exception as e:
        # Log but don't fail frontend
        print(f"[WARN] Failed to delete namespace {namespace}: {e}")

    return {"message": "Chat memory cleared"}

