import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX")

def web_search(query: str, num_results: int = 5):
    """Perform Google Search and return structured results."""
    if not GOOGLE_API_KEY or not GOOGLE_SEARCH_CX:
        raise ValueError("Missing GOOGLE_API_KEY or GOOGLE_SEARCH_CX in environment variables.")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_SEARCH_CX,
        "q": query,
        "num": num_results,
        "hl": "en",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    items = []
    for item in data.get("items", []):
        items.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "link": item.get("link")
        })
    return items
