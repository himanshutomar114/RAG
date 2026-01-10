import requests
from bs4 import BeautifulSoup

MAX_HTML_CHARS = 300_000  # 🔥 CRITICAL MEMORY SAFETY

def load_from_url(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch URL: {e}")

    # 🔥 LIMIT RAW HTML SIZE (MOST IMPORTANT LINE)
    html = response.text[:MAX_HTML_CHARS]

    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # Clean empty lines
    return "\n".join(
        line.strip()
        for line in text.splitlines()
        if line.strip()
    )
