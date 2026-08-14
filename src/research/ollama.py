from __future__ import annotations

import json
from time import perf_counter
from typing import Any

import httpx

from .performance import ResearchPerformance


class OllamaProvider:
    """
    Local Ollama adapter.

    Uses one persistent HTTPX client so repeated
    requests can reuse connections.

    Ollama's native generation metrics are preserved
    for performance analysis.
    """

    def __init__(
        self,
        *,
        model: str = "qwen3:4b",
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 120.0,
        max_output_tokens: int = 768,
        keep_alive: str | int = "10m",
        num_ctx: int | None = None,
        performance: ResearchPerformance | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero."
            )

        if max_output_tokens < 1:
            raise ValueError(
                "max_output_tokens must be >= 1."
            )

        if num_ctx is not None and num_ctx < 1:
            raise ValueError(
                "num_ctx must be >= 1."
            )

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_output_tokens = max_output_tokens
        self.keep_alive = keep_alive
        self.num_ctx = num_ctx
        self.performance = performance

        self._client = httpx.Client(
            timeout=httpx.Timeout(
                timeout_seconds,
                connect=min(
                    10.0,
                    timeout_seconds,
                ),
            ),
            limits=httpx.Limits(
                max_connections=16,
                max_keepalive_connections=8,
                keepalive_expiry=30.0,
            ),
        )

    def generate_json(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:

        if not prompt.strip():
            raise ValueError(
                "prompt is required."
            )

        if not isinstance(schema, dict):
            raise TypeError(
                "schema must be a dictionary."
            )

        options: dict[str, Any] = {
            "temperature": 0,
            "num_predict": self.max_output_tokens,
        }

        if self.num_ctx is not None:
            options["num_ctx"] = self.num_ctx

        payload = {
            "model": self.model,
            "stream": False,
            "think": False,
            "keep_alive": self.keep_alive,
            "format": schema,
            "options": options,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return only JSON matching "
                        "the supplied schema. "
                        "Do not explain your reasoning."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        }

        started_at = perf_counter()

        try:
            response = self._client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Ollama request failed: {exc}"
            ) from exc

        http_seconds = (
            perf_counter() - started_at
        )

        data = response.json()

        message = data.get(
            "message",
            {},
        )

        content = message.get(
            "content",
            "",
        )

        if not isinstance(content, str):
            raise ValueError(
                "Ollama response content must be a string."
            )

        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Ollama returned invalid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise ValueError(
                "Ollama JSON response must be an object."
            )

        performance = self.performance

        if performance is not None:

            billion = 1_000_000_000

            performance.record_llm(
                http_seconds=http_seconds,
                total_seconds=(
                    float(
                        data.get(
                            "total_duration",
                            0,
                        )
                    )
                    / billion
                ),
                load_seconds=(
                    float(
                        data.get(
                            "load_duration",
                            0,
                        )
                    )
                    / billion
                ),
                prompt_eval_seconds=(
                    float(
                        data.get(
                            "prompt_eval_duration",
                            0,
                        )
                    )
                    / billion
                ),
                generation_seconds=(
                    float(
                        data.get(
                            "eval_duration",
                            0,
                        )
                    )
                    / billion
                ),
                prompt_tokens=int(
                    data.get(
                        "prompt_eval_count",
                        0,
                    )
                    or 0
                ),
                output_tokens=int(
                    data.get(
                        "eval_count",
                        0,
                    )
                    or 0
                ),
                prompt_characters=len(prompt),
                response_characters=len(content),
                model=self.model,
            )

        return result

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.close()
