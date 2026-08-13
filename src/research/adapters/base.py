from __future__ import annotations

from typing import Protocol

from research.reachability import (
    BackendHealth,
    ReachabilityResult,
)


class ResearchSourceAdapter(Protocol):
    """Platform adapter contract."""

    name: str

    def supports(self, source_url: str) -> bool:
        ...

    def read(self, source_url: str) -> ReachabilityResult:
        ...

    def health(self) -> BackendHealth:
        ...
