from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from services.document_loader import load_document
from services.vector_store import store_chunks, query_chunks
from services.rag_chain import generate_answer
from services.url_loader import load_from_url
from dotenv import load_dotenv
load_dotenv(".env")

app = FastAPI()

class ChatRequest(BaseModel):
    query: str

class URLRequest(BaseModel):
    url: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    text = load_document(file)
    store_chunks(text)
    return {"message": "File indexed successfully"}

@app.post("/ingest-url")
async def ingest_url(data: URLRequest):
    text = load_from_url(data.url)
    store_chunks(text)
    return {"message": "URL indexed successfully"}

@app.post("/chat")
async def chat(data: ChatRequest):
    docs = query_chunks(data.query)
    answer = generate_answer(data.query, docs)
    return {"answer": answer}
