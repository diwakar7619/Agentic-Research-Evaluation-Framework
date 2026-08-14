from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SourceAccounting:
    requested: int = 0
    discovered: int = 0
    duplicate: int = 0
    fetch_attempted: int = 0
    fetch_succeeded: int = 0
    fetch_failed: int = 0
    evidence_bearing: int = 0
    unique_evidence_sources: set[str] = field(
        default_factory=set,
    )

    def record_discovered(self, count: int = 1) -> None:
        self.discovered += count

    def record_duplicate(self, count: int = 1) -> None:
        self.duplicate += count

    def record_fetch_attempt(self, count: int = 1) -> None:
        self.fetch_attempted += count

    def record_fetch_success(
        self,
        source_id: str | None = None,
    ) -> None:
        self.fetch_succeeded += 1

        if source_id:
            self.unique_evidence_sources.add(source_id)

    def record_fetch_failure(self, count: int = 1) -> None:
        self.fetch_failed += count

    def record_evidence(
        self,
        source_id: str | None = None,
    ) -> None:
        self.evidence_bearing += 1

        if source_id:
            self.unique_evidence_sources.add(source_id)

    def summary(self) -> dict[str, object]:
        return {
            "requested": self.requested,
            "discovered": self.discovered,
            "duplicate": self.duplicate,
            "fetch_attempted": self.fetch_attempted,
            "fetch_succeeded": self.fetch_succeeded,
            "fetch_failed": self.fetch_failed,
            "evidence_bearing": self.evidence_bearing,
            "unique_evidence_sources": len(
                self.unique_evidence_sources
            ),
        }
