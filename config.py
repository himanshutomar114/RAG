from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
VECTOR_DB_PATH = "vector_db"

if not HUGGINGFACEHUB_API_TOKEN:
    raise RuntimeError("HUGGINGFACEHUB_API_TOKEN not found. Check .env file.")