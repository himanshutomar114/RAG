import requests, os

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """
You are a document question-answering assistant.

RULES:
- Answer ONLY using the provided context.
- Carefully scan the context for any keywords, phrases, or partial information related to the question.
- If relevant keywords or partial information are found, use them to construct the best possible answer.
- You are allowed to infer connections ONLY from the given context (do NOT use external knowledge).
- If the answer is partially available, provide a meaningful answer based on available information.
- Only say "I could not find this information in the uploaded document or URL." if absolutely no relevant keywords or information exist in the context.
- Do NOT hallucinate or add information not present in the context.
- Keep answers clear, concise, and structured if needed.
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
    res = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-analyzer-omega.vercel.app", 
            "X-Title": "AI Analyzer",
        },
        json={
            "model": "openai/gpt-3.5-turbo",  # Changed to a known available model
            "messages": messages,
            "temperature": 0.2,   # 🔥 LOW = factual answers
            "max_tokens": 400
        },
        timeout=60
    )

    print(f"OpenRouter response: {res.status_code} {res.text}")  # Debug output
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"].strip()
