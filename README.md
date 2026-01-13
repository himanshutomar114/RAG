# RAG Document Q&A Backend

A powerful **Retrieval-Augmented Generation (RAG)** API backend built with FastAPI. Upload documents or ingest URLs, then ask questions about them using AI-powered answers grounded in your data.

## 🌟 Features

- **Multi-format Document Support**: PDF, DOCX, and web URLs
- **Smart Text Chunking**: Intelligent document splitting for better retrieval
- **Vector Search**: Pinecone-powered semantic search
- **AI-Powered Answers**: OpenRouter integration with LLM support
- **Per-Chat Namespaces**: Isolated document storage per conversation
- **Token-Based Rate Limiting**: Protect API from abuse (5/10/30 requests per minute)
- **CORS Enabled**: Ready for frontend integration
- **Asynchronous Processing**: Non-blocking background tasks for fast responses
- **Document Management**: Upload, ingest URLs, and delete specific documents

## 🏗️ Architecture

```
┌─────────────┐
│  FastAPI    │
│  App        │
├─────────────┤
│  Endpoints  │
│  - /upload  │
│  - /ingest  │
│  - /chat    │
│  - /delete  │
└──────┬──────┘
       │
   ┌───┴────────────┬──────────────┐
   │                │              │
┌──▼──┐      ┌──────▼──┐    ┌─────▼────┐
│ PDF │      │ Chunker │    │  Vector  │
│DOCX │      │         │    │  Store   │
└─────┘      └────┬────┘    │(Pinecone)│
                  │         └──────────┘
                  │
            ┌─────▼──────┐
            │ Embeddings │
            │(HuggingFace)│
            └─────┬──────┘
                  │
            ┌─────▼──────┐
            │ LLM Query  │
            │(OpenRouter)│
            └────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- Pinecone API key
- OpenRouter API key
- HuggingFace account (for embeddings)

## 🚀 Installation

### 1. Clone & Setup

```bash
git clone <your-repo>
cd RAG
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory:

```env
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=your_pinecone_index_name
OPENROUTER_API_KEY=your_openrouter_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

### 3. Run Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

## 📡 API Endpoints

### 1. Upload Document

Upload a PDF or DOCX file to index.

```http
POST /upload?chat_id=<chat_id>
Header: X-Token: <your-api-token>
Body: multipart/form-data with file
```

**Response:**

```json
{
  "status": "success",
  "chunks_indexed": 45
}
```

**Rate Limit:** 5 requests/minute per token

---

### 2. Ingest URL

Extract and index content from a URL.

```http
POST /ingest-url?chat_id=<chat_id>
Header: X-Token: <your-api-token>
Body: {
  "url": "https://example.com/article"
}
```

**Response:**

```json
{
  "message": "URL indexed successfully",
  "chunks_indexed": 32
}
```

**Rate Limit:** 10 requests/minute per token

---

### 3. Chat / Ask Questions

Query your indexed documents.

```http
POST /chat?chat_id=<chat_id>
Header: X-Token: <your-api-token>
Body: {
  "query": "What is the main topic of the document?"
}
```

**Response:**

```json
{
  "answer": "The document discusses the history of artificial intelligence..."
}
```

**Rate Limit:** 30 requests/minute per token

---

### 4. Clear Chat Memory

Delete all documents in a chat namespace.

```http
POST /clear-chat?chat_id=<chat_id>
Header: X-Token: <your-api-token>
```

**Response:**

```json
{
  "message": "Chat memory cleared"
}
```

---

## 🔑 Key Components

### Services

| File                 | Purpose                               |
| -------------------- | ------------------------------------- |
| `document_loader.py` | Load & extract text from PDF/DOCX     |
| `url_loader.py`      | Fetch & parse web content             |
| `chunker.py`         | Split text into optimal chunks        |
| `embeddings.py`      | Generate vector embeddings            |
| `vector_store.py`    | Store/query vectors in Pinecone       |
| `rag_chain.py`       | LLM orchestration & answer generation |

### Rate Limiting

Token-based rate limiter with sliding window:

- **Upload**: 5 requests/minute
- **Ingest URL**: 10 requests/minute
- **Chat**: 30 requests/minute

Exceeding limits returns HTTP 429 with clear error message.

### Namespace Strategy

Each chat conversation is isolated using the pattern:

```
namespace = "{x_token}:{chat_id}"
```

This ensures multi-user safety and conversation isolation.

## 🌐 Frontend Integration

### Example: Upload & Chat

```javascript
// 1. Upload document
const formData = new FormData();
formData.append("file", pdfFile);

const uploadRes = await fetch("http://localhost:8000/upload?chat_id=conv-123", {
  method: "POST",
  headers: { "X-Token": "user-token-abc123" },
  body: formData,
});

// 2. Ask question
const chatRes = await fetch("http://localhost:8000/chat?chat_id=conv-123", {
  method: "POST",
  headers: {
    "X-Token": "user-token-abc123",
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ query: "What is the summary?" }),
});

const { answer } = await chatRes.json();
console.log(answer);
```

## 🔐 Security

- ✅ Token-based authentication via `X-Token` header
- ✅ Rate limiting prevents abuse
- ✅ CORS configured for allowed origins
- ✅ Input validation with Pydantic
- ✅ Namespace isolation per user/chat

## 📊 Performance

- **Async Processing**: Upload/ingest run in background
- **Chunking**: Max 100 chunks per upload for efficiency
- **Batched Upserts**: Pinecone operations batched in groups of 50
- **Vector Caching**: Embeddings cached per request

## 🚢 Deployment

### Render

1. Add `runtime.txt`:

```
python-3.11.9
```

2. Set environment variables in Render dashboard

3. Deploy:

```bash
git push origin main
```

### Environment-Specific Configuration

```python
# For development
ALLOWED_ORIGINS = ["http://localhost:3000"]

# For production
ALLOWED_ORIGINS = ["https://ai-analyzer-omega.vercel.app"]
```

## 🔧 Troubleshooting

### "No documents found" error

- Ensure document was successfully uploaded
- Check chat_id matches between upload and query
- Verify token is consistent

### Rate limit exceeded

- Implement exponential backoff on frontend
- Check token is per-user (not shared)

### Embedding errors

- Verify HuggingFace API key is set
- Check internet connectivity
- Model may be loading on first call (slower)

### Pinecone connection failed

- Verify API key and index name in `.env`
- Check index is in correct region
- Ensure namespace exists before querying

## 📚 API Response Codes

| Code | Meaning                         |
| ---- | ------------------------------- |
| 200  | Success                         |
| 400  | Invalid request (e.g., bad URL) |
| 429  | Rate limit exceeded             |
| 500  | Server error                    |

## 📦 Dependencies

- **FastAPI**: Modern async web framework
- **Pinecone**: Vector database
- **LangChain**: Text splitting & LLM tools
- **HuggingFace**: Embeddings
- **PyPDF2**: PDF parsing
- **BeautifulSoup4**: Web scraping
- **OpenRouter**: LLM API

## 📝 Configuration

Key constants in `services/vector_store.py`:

```python
MAX_CHUNKS = 100          # Max chunks per upload
UPSERT_BATCH_SIZE = 50    # Batch size for Pinecone
```

## 🎯 Future Enhancements

- [ ] Document metadata tracking (title, date, source)
- [ ] Conversation history endpoint
- [ ] Multiple LLM providers
- [ ] Custom chunk size configuration
- [ ] Document similarity search
- [ ] Feedback/rating system

## 📄 License

MIT License - see LICENSE file

## 🤝 Support

For issues, email or create a GitHub issue with:

- Error message
- Steps to reproduce
- Environment details

---

**Built with ❤️ using FastAPI + Pinecone + OpenRouter**
