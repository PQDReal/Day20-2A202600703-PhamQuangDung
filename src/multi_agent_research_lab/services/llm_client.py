"""LLM client abstraction.

Production note: agents depend on this interface instead of importing an SDK directly.
When an API key is unavailable, the client returns a deterministic local completion so
the lab can be tested offline.
"""

from dataclasses import dataclass
from importlib import import_module
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from multi_agent_research_lab.core.config import Settings, get_settings


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client with OpenAI support and offline fallback."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion.

        Uses OpenAI when `OPENAI_API_KEY` and the package are available; otherwise
        produces a concise deterministic response. Retry, timeout, and coarse token
        accounting stay here so agents remain provider-agnostic.
        """

        if self.settings.openai_api_key:
            return self._complete_openai(system_prompt, user_prompt)
        return self._complete_offline(system_prompt, user_prompt)

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, min=0.5, max=2))
    def _complete_openai(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        openai_module = import_module("openai")
        client_cls: Any = openai_module.OpenAI
        client = client_cls(
            api_key=self.settings.openai_api_key, timeout=self.settings.timeout_seconds
        )
        response = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "prompt_tokens", None)
        output_tokens = getattr(usage, "completion_tokens", None)
        cost = self._estimate_cost(input_tokens, output_tokens)
        return LLMResponse(
            content=content, input_tokens=input_tokens, output_tokens=output_tokens, cost_usd=cost
        )

    def _complete_offline(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        words = (system_prompt + " " + user_prompt).split()
        query_line = next((line for line in user_prompt.splitlines() if line.strip()), user_prompt)
        content = (
            "Offline synthesis: "
            f"{query_line[:180]}. "
            "Key response should separate evidence collection, analysis, and final writing; "
            "include citations where sources are present; and call out limitations explicitly."
        )
        output_tokens = max(20, len(content.split()))
        return LLMResponse(
            content=content,
            input_tokens=max(1, len(words)),
            output_tokens=output_tokens,
            cost_usd=0.0,
        )

    @staticmethod
    def _estimate_cost(input_tokens: int | None, output_tokens: int | None) -> float | None:
        if input_tokens is None or output_tokens is None:
            return None
        # Coarse gpt-4o-mini style estimate: $0.15/M input, $0.60/M output.
        return (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)
