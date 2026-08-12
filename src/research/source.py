from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SourceCandidate:
    source_id: str
    source_type: str
    title: str
    url: str
    metadata: dict


@dataclass(frozen=True)
class CollectedSource:
    source_id: str
    source_type: str
    title: str
    url: str
    content: str
    metadata: dict


class SourceDiscoverer(Protocol):

    def discover(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[SourceCandidate]:
        ...


class SourceCollector(Protocol):

    def collect(
        self,
        candidate: SourceCandidate,
    ) -> CollectedSource:
        ...
