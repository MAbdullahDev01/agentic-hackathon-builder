from collections.abc import Callable
from src.tools.web_search import web_search
from typing import Any

tool_registry: dict[str, Callable[..., Any]] = {
    "web_search" : web_search,
}

if __name__ == "__main__":
    pass