import json
from tavily import TavilyClient
from src.config import settings

tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

def web_search(queries: list[dict[str, str]], max_query: int = 5) -> str:
    if not queries:
        raise ValueError("Search queries cannot be empty.")

    all_results = []
    max_results_clamped = max(1, min(max_query, 5))
    
    for query_dict in queries:
        query_text = query_dict.get("query")
        if not query_text:
            continue

        response = tavily_client.search(query=query_text, max_results=max_results_clamped)

        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content")
            })
        all_results.append(results)

    return json.dumps(all_results, ensure_ascii=False)

if __name__ == "__main__":
    results = web_search([{"category": "Health risks", "query": "NASA astronaut health monitoring research"}])
    print(results)