"""Make one small, real call to each provider to check your API keys work.

Usage:
    python -m pipeline.check_providers

Costs a fraction of a cent. Needs OPENROUTER_API_KEY and TAVILY_API_KEY set.
"""

import sys

from pipeline.providers import OpenRouterLLM, ProviderError, ReadabilityFetch, TavilySearch

# OpenRouter's auto-router picks a model for us; fine for a one-line test.
CHECK_MODEL = "openrouter/auto"


def main() -> int:
    ok = True

    print("1. Search (Tavily)...")
    results = []
    try:
        results = TavilySearch(max_results=3, search_depth="basic").search("ASML EUV lithography market share")
        print(f"   OK: {len(results)} results, first: {results[0].url if results else '(none)'}")
    except ProviderError as e:
        ok = False
        print(f"   FAILED: {e}")

    print("2. Fetch (requests + readability)...")
    url = results[0].url if results else "https://en.wikipedia.org/wiki/Extreme_ultraviolet_lithography"
    try:
        text = ReadabilityFetch().fetch(url)
        print(f"   OK: {len(text):,} characters from {url}")
    except ProviderError as e:
        ok = False
        print(f"   FAILED: {e}")

    print("3. LLM (OpenRouter)...")
    try:
        reply = OpenRouterLLM().complete("Reply with exactly the word: ready", model=CHECK_MODEL)
        print(f"   OK: model replied {reply.strip()[:40]!r}")
    except ProviderError as e:
        ok = False
        print(f"   FAILED: {e}")

    print("\nAll providers working." if ok else "\nSome providers failed; see above.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
