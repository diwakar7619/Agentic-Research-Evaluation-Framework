from __future__ import annotations

import json
from typing import Any

import httpx


class OllamaProvider:
    """
    Local Ollama adapter.

    The research engine depends only on the provider contract,
    never on Ollama-specific response structures.
    """

    def __init__(
        self,
        *,
        model: str = "qwen3:4b",
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 120.0,
        max_output_tokens: int = 768,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero."
            )

        if max_output_tokens < 1:
            raise ValueError(
                "max_output_tokens must be >= 1."
            )

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_output_tokens = max_output_tokens

    def generate_json(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        if not prompt.strip():
            raise ValueError("prompt is required.")

        if not isinstance(schema, dict):
            raise TypeError("schema must be a dictionary.")

        payload = {
            "model": self.model,
            "stream": False,
            "think": False,
            "format": schema,
            "options": {
                "temperature": 0,
                "num_predict": self.max_output_tokens,
            },
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return only JSON matching the supplied schema. "
                        "Do not explain your reasoning."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        }

        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Ollama request failed: {exc}"
            ) from exc

        data = response.json()

        message = data.get("message", {})
        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(
                "Ollama returned no structured content."
            )

        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Ollama returned invalid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise RuntimeError(
                "Ollama structured response must be a JSON object."
            )

        return result
