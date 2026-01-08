from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from pydantic import BaseModel
from services.document_loader import load_document
from services.vector_store import store_chunks, query_chunks
from services.rag_chain import generate_answer
from services.url_loader import load_from_url
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from collections import defaultdict
import time

load_dotenv(".env")

app = FastAPI()

# Token-based rate limiter
class TokenRateLimiter:
    def __init__(self):
        self.token_requests = defaultdict(list)
    
    def is_allowed(self, token: str, limit: int, window_seconds: int = 60) -> bool:
        now = time.time()
        cutoff = now - window_seconds
        
        # Clean old requests
        self.token_requests[token] = [req_time for req_time in self.token_requests[token] if req_time > cutoff]
        
        if len(self.token_requests[token]) < limit:
            self.token_requests[token].append(now)
            return True
        return False

limiter = TokenRateLimiter()

class ChatRequest(BaseModel):
    query: str

class URLRequest(BaseModel):
    url: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), x_token: str = Header(...)):
    if not limiter.is_allowed(x_token, limit=5):
        raise HTTPException(status_code=429, detail="Rate limit exceeded: 5 requests per minute")
    text = load_document(file)
    store_chunks(text)
    return {"message": "File indexed successfully"}

@app.post("/ingest-url")
async def ingest_url(data: URLRequest, x_token: str = Header(...)):
    if not limiter.is_allowed(x_token, limit=10):
        raise HTTPException(status_code=429, detail="Rate limit exceeded: 10 requests per minute")
    text = load_from_url(data.url)
    store_chunks(text)
    return {"message": "URL indexed successfully"}

@app.post("/chat")
async def chat(data: ChatRequest, x_token: str = Header(...)):
    if not limiter.is_allowed(x_token, limit=30):
        raise HTTPException(status_code=429, detail="Rate limit exceeded: 30 requests per minute")
    docs = query_chunks(data.query)
    answer = generate_answer(data.query, docs)
    return {"answer": answer}
