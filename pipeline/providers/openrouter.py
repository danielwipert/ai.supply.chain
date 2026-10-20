"""LLMProvider backed by OpenRouter (https://openrouter.ai/docs)."""

import os

import requests

from pipeline.providers.base import ProviderError

API_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterLLM:
    def __init__(self, api_key: str | None = None, session: requests.Session | None = None,
                 timeout: float = 120, system_prompt: str | None = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ProviderError("OPENROUTER_API_KEY is not set (see README: 'API keys')")
        self.session = session or requests.Session()
        self.timeout = timeout
        self.system_prompt = system_prompt

    def complete(self, prompt: str, model: str) -> str:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        resp = self.session.post(
            API_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": model, "messages": messages, "temperature": 0},
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise ProviderError(f"OpenRouter returned HTTP {resp.status_code}: {resp.text[:300]}")

        body = resp.json()
        if "error" in body:
            raise ProviderError(f"OpenRouter error: {body['error']}")
        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise ProviderError(f"Unexpected OpenRouter response: {str(body)[:300]}") from e
