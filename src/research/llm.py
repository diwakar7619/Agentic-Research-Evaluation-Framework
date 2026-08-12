from __future__ import annotations

from typing import Any, Protocol


class LLMProvider(Protocol):
    """Minimal provider boundary used by research intelligence."""

    def generate_json(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        ...
