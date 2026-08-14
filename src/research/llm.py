from __future__ import annotations

from typing import Any, Protocol

from .performance import ResearchPerformance


class LLMProvider(Protocol):
    """Minimal provider boundary used by research intelligence."""

    def generate_json(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        performance: ResearchPerformance | None = None,
    ) -> dict[str, Any]:
        ...
