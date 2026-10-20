"""FetchProvider: plain requests + readability extraction (spec 6.3)."""

import re

import lxml.html
import requests
from readability import Document

from pipeline.providers.base import ProviderError

USER_AGENT = "Mozilla/5.0 (compatible; AISupplyChainMap/0.1; research pipeline)"


class ReadabilityFetch:
    def __init__(self, session: requests.Session | None = None, timeout: float = 30,
                 max_chars: int = 50_000):
        self.session = session or requests.Session()
        self.timeout = timeout
        self.max_chars = max_chars  # keep LLM prompts a sane size

    def fetch(self, url: str) -> str:
        try:
            resp = self.session.get(url, headers={"User-Agent": USER_AGENT}, timeout=self.timeout)
        except requests.RequestException as e:
            raise ProviderError(f"Could not fetch {url}: {e}") from e
        if resp.status_code != 200:
            raise ProviderError(f"Fetching {url} returned HTTP {resp.status_code}")

        content_type = resp.headers.get("Content-Type", "")
        if "html" not in content_type and "text/plain" not in content_type:
            # PDFs (filings, analyst reports) are not handled yet.
            raise ProviderError(f"{url} is '{content_type}', only HTML and plain text are supported")
        if "text/plain" in content_type:
            return resp.text[: self.max_chars]

        return html_to_text(resp.text)[: self.max_chars]


def html_to_text(html: str) -> str:
    """Pull the main article out of a page and return it as plain text."""
    doc = Document(html)
    tree = lxml.html.fromstring(doc.summary())
    for block in tree.iter("p", "li", "h1", "h2", "h3", "h4", "tr", "br"):
        block.tail = "\n" + (block.tail or "")
    text = tree.text_content()
    title = doc.title().strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    return f"{title}\n\n{text}" if title else text
