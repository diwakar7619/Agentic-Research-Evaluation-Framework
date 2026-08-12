from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchStep:
    """
    One independently researchable sub-question.
    """

    id: str
    question: str
    source_types: tuple[str, ...]
    expected_evidence: str
    priority: int = 1

    def validate(self) -> None:
        if not self.id.strip():
            raise ValueError("ResearchStep.id cannot be empty.")

        if not self.question.strip():
            raise ValueError(
                "ResearchStep.question cannot be empty."
            )

        if not self.source_types:
            raise ValueError(
                "ResearchStep must define source_types."
            )

        if not self.expected_evidence.strip():
            raise ValueError(
                "ResearchStep.expected_evidence cannot be empty."
            )

        if self.priority < 1:
            raise ValueError(
                "ResearchStep.priority must be >= 1."
            )


@dataclass(frozen=True)
class ResearchPlan:
    """
    Structured plan produced before research execution.

    This is deliberately independent of any LLM provider.
    """

    question: str
    steps: tuple[ResearchStep, ...]

    def validate(self) -> None:
        if not self.question.strip():
            raise ValueError(
                "ResearchPlan.question cannot be empty."
            )

        if not self.steps:
            raise ValueError(
                "ResearchPlan must contain at least one step."
            )

        ids: set[str] = set()

        for step in self.steps:
            step.validate()

            if step.id in ids:
                raise ValueError(
                    f"Duplicate ResearchStep id: {step.id}"
                )

            ids.add(step.id)
