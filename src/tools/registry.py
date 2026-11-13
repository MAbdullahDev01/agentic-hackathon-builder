from src.tools.web_search import web_search

tools: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search for information on the web",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Web search query"
                    },
                    "max_query": {
                        "type": "integer",
                        "description": "Maximum number of results (1-5)"
                    }
                },
                "required": ["query"],
                "additional_properties": False
            }
        }
    },
]

tool_registry = {
    "web_search" : web_search,
}