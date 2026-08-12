from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SynthesisClaim:
    claim_id: str
    text: str
    evidence_ids: tuple[str, ...]
    support_status: str

    def validate(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("claim_id cannot be empty.")

        if not self.text.strip():
            raise ValueError("claim text cannot be empty.")

        allowed = {
            "insufficient",
            "single_source",
            "corroborated",
        }

        if self.support_status not in allowed:
            raise ValueError(
                f"Invalid support_status: {self.support_status}"
            )


@dataclass(frozen=True)
class ResearchSynthesis:
    question: str
    answer: str
    claims: tuple[SynthesisClaim, ...]
    evidence_ids: tuple[str, ...]
    sources_used: int

    def validate(self) -> None:
        if not self.question.strip():
            raise ValueError("question cannot be empty.")

        if not self.answer.strip():
            raise ValueError("answer cannot be empty.")

        if self.sources_used < 0:
            raise ValueError(
                "sources_used cannot be negative."
            )

        for claim in self.claims:
            claim.validate()

        known_evidence = set(self.evidence_ids)

        for claim in self.claims:
            unknown = (
                set(claim.evidence_ids)
                - known_evidence
            )

            if unknown:
                raise ValueError(
                    "Claim references unknown evidence IDs: "
                    + ", ".join(sorted(unknown))
                )
