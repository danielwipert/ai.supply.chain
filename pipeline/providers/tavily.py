"""SearchProvider backed by Tavily (https://docs.tavily.com). Chosen at the 2026-10-20 gate."""

import os

import requests

from pipeline.providers.base import ProviderError, Result

API_URL = "https://api.tavily.com/search"


class TavilySearch:
    def __init__(self, api_key: str | None = None, session: requests.Session | None = None,
                 max_results: int = 5, search_depth: str = "advanced", timeout: float = 60):
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY")
        if not self.api_key:
            raise ProviderError("TAVILY_API_KEY is not set (see README: 'API keys')")
        self.session = session or requests.Session()
        self.max_results = max_results
        self.search_depth = search_depth
        self.timeout = timeout

    def search(self, query: str) -> list[Result]:
        resp = self.session.post(
            API_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "query": query,
                "max_results": self.max_results,
                "search_depth": self.search_depth,
                "include_raw_content": True,
            },
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise ProviderError(f"Tavily returned HTTP {resp.status_code}: {resp.text[:300]}")

        return [
            Result(
                title=r.get("title", ""),
                url=r["url"],
                snippet=r.get("content", ""),
                content=r.get("raw_content") or "",
                score=r.get("score"),
            )
            for r in resp.json().get("results", [])
            if r.get("url")
        ]
