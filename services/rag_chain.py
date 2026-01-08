import requests, os

def generate_answer(question: str, context_docs: list[str]):
    prompt = f"""
Answer using context only.

Context:
{chr(10).join(context_docs)}

Question:
{question}
"""

    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "model": "mistralai/mistral-7b-instruct",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    return res.json()["choices"][0]["message"]["content"]
