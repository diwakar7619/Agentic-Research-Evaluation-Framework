from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchEvidence:

    source_id: str
    source_url: str
    text: str
    relevance: float = 0.0


@dataclass(frozen=True)
class ResearchResult:

    question: str
    answer: dict
    evidence: tuple[ResearchEvidence, ...]
    sources_considered: int
    sources_collected: int
