import json
from tavily import TavilyClient
from src.config import settings

tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

def web_search(query: str, max_query: int = 5) -> str:
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    response = tavily_client.search(query=query, max_results=max(1, min(max_query, 5)))

    results: list = []

    for item in response.get("results", []):
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "content": item.get("content")
        })

    return json.dumps(results, ensure_ascii=False)

if __name__ == "__main__":
    results = web_search("NASA astronaut health monitoring research")
    print(results)