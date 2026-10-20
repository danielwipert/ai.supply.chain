"""Tests for pipeline/providers. A fake session stands in for the network, so no keys are needed."""

import pytest

from pipeline.providers import OpenRouterLLM, ProviderError, ReadabilityFetch, Result, TavilySearch


class FakeResponse:
    def __init__(self, status_code=200, json_body=None, text="", headers=None):
        self.status_code = status_code
        self._json = json_body
        self.text = text
        self.headers = headers or {}

    def json(self):
        return self._json


class FakeSession:
    """Records each request and returns a canned response."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        return self.response

    def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        return self.response


# --- OpenRouter -------------------------------------------------------------

def test_openrouter_returns_message_text():
    session = FakeSession(FakeResponse(json_body={"choices": [{"message": {"content": "hello"}}]}))
    llm = OpenRouterLLM(api_key="k", session=session)
    assert llm.complete("hi", model="some/model") == "hello"

    _, url, kwargs = session.calls[0]
    assert url.endswith("/chat/completions")
    assert kwargs["headers"]["Authorization"] == "Bearer k"
    assert kwargs["json"]["model"] == "some/model"
    assert kwargs["json"]["messages"][-1] == {"role": "user", "content": "hi"}


def test_openrouter_http_error_raises():
    llm = OpenRouterLLM(api_key="k", session=FakeSession(FakeResponse(401, text="bad key")))
    with pytest.raises(ProviderError, match="401"):
        llm.complete("hi", model="m")


def test_openrouter_missing_key_raises(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="OPENROUTER_API_KEY"):
        OpenRouterLLM()


# --- Tavily -----------------------------------------------------------------

def test_tavily_maps_results():
    body = {"results": [
        {"title": "HBM market", "url": "https://a.com", "content": "snip", "raw_content": "full", "score": 0.9},
        {"title": "No raw", "url": "https://b.com", "content": "snip2", "raw_content": None},
    ]}
    session = FakeSession(FakeResponse(json_body=body))
    results = TavilySearch(api_key="k", session=session).search("hbm market share")

    assert results == [
        Result(title="HBM market", url="https://a.com", snippet="snip", content="full", score=0.9),
        Result(title="No raw", url="https://b.com", snippet="snip2", content="", score=None),
    ]
    assert session.calls[0][2]["json"]["query"] == "hbm market share"


def test_tavily_missing_key_raises(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="TAVILY_API_KEY"):
        TavilySearch()


# --- Fetch ------------------------------------------------------------------

PAGE = """<html><head><title>HBM Report</title></head><body>
<nav>Home | About | Login</nav>
<article><h1>HBM Report</h1>
<p>SK Hynix led the high-bandwidth memory market in 2026, according to the report.</p>
<p>Samsung and Micron are the other two makers of HBM, and both are adding capacity this year.</p>
</article><footer>Copyright</footer></body></html>"""


def test_fetch_extracts_article_text():
    session = FakeSession(FakeResponse(text=PAGE, headers={"Content-Type": "text/html; charset=utf-8"}))
    text = ReadabilityFetch(session=session).fetch("https://example.com/hbm")
    assert text.startswith("HBM Report")
    assert "SK Hynix led" in text
    assert "Micron are the other two" in text
    assert "<p>" not in text


def test_fetch_rejects_pdf():
    session = FakeSession(FakeResponse(text="%PDF", headers={"Content-Type": "application/pdf"}))
    with pytest.raises(ProviderError, match="application/pdf"):
        ReadabilityFetch(session=session).fetch("https://example.com/report.pdf")


def test_fetch_http_error_raises():
    session = FakeSession(FakeResponse(404, headers={"Content-Type": "text/html"}))
    with pytest.raises(ProviderError, match="404"):
        ReadabilityFetch(session=session).fetch("https://example.com/missing")
