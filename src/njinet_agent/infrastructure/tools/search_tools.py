from langchain_tavily import TavilySearch

from njinet_agent.core.config import Settings


def build_tavily_search_tool(_: Settings) -> TavilySearch:
    return TavilySearch(max_results=5)
