import requests, os

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """
You are a document question-answering assistant.

RULES:
- Answer ONLY using the provided context.
- If the answer is NOT present in the context, say:
  "I could not find this information in the uploaded document or URL."
- Do NOT use external knowledge.
- Do NOT guess or hallucinate.
- Keep answers clear and concise.
"""

def generate_answer(question: str, context_docs: list[str]) -> str:
    context = "\n\n".join(context_docs)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
Context:
{context}

Question:
{question}

Answer:
"""
        }
    ]

    api_key = os.getenv('OPENROUTER_API_KEY')
    print(f"OPENROUTER_API_KEY: {api_key}")  # Debug output
    res = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-analyzer-omega.vercel.app", 
            "X-Title": "AI Analyzer",
        },
        json={
            "model": "mistralai/mistral-7b-instruct",
            "messages": messages,
            "temperature": 0.2,   # 🔥 LOW = factual answers
            "max_tokens": 400
        },
        timeout=60
    )

    print(f"OpenRouter response: {res.status_code} {res.text}")  # Debug output
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"].strip()
