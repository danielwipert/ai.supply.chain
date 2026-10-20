"""The three provider interfaces (spec 6.3).

The pipeline only talks to these interfaces, so any implementation can be
swapped in (a different search API, a fake for tests) without touching it.
"""

from dataclasses import dataclass
from typing import Protocol


class ProviderError(Exception):
    """A provider call failed (missing key, HTTP error, bad response)."""


@dataclass
class Result:
    """One search result."""
    title: str
    url: str
    snippet: str            # short extract chosen by the search API
    content: str = ""       # full page text, when the search API returns it
    score: float | None = None


class LLMProvider(Protocol):
    def complete(self, prompt: str, model: str) -> str: ...


class SearchProvider(Protocol):
    def search(self, query: str) -> list[Result]: ...


class FetchProvider(Protocol):
    def fetch(self, url: str) -> str: ...
