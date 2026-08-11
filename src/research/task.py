from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ResearchTask:
    """
    Configuration for one research question.

    The research engine remains source-agnostic.
    A task decides what to research, which source types are allowed,
    and what structured information should be extracted.
    """

    name: str
    question: str
    source_types: tuple[str, ...]
    extraction_schema: dict[str, Any]

    metadata: dict[str, Any] = field(default_factory=dict)

    def supports_source(self, source_type: str) -> bool:
        return source_type in self.source_types

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("ResearchTask.name cannot be empty.")

        if not self.question.strip():
            raise ValueError("ResearchTask.question cannot be empty.")

        if not self.source_types:
            raise ValueError("ResearchTask must define at least one source type.")

        if not isinstance(self.extraction_schema, dict):
            raise TypeError("extraction_schema must be a dictionary.")
