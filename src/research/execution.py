from __future__ import annotations

from dataclasses import dataclass

from research.plan import ResearchStep
from research.result import ResearchResult


@dataclass(frozen=True)
class StepExecution:
    step: ResearchStep
    status: str
    attempts: int
    result: ResearchResult | None = None
    error: str | None = None

    def validate(self) -> None:
        if self.status not in {
            "completed",
            "failed",
        }:
            raise ValueError(
                f"Invalid step execution status: {self.status}"
            )

        if self.attempts < 1:
            raise ValueError(
                "StepExecution.attempts must be >= 1."
            )

        if self.status == "completed":
            if self.result is None:
                raise ValueError(
                    "Completed step must contain a result."
                )

            if self.error is not None:
                raise ValueError(
                    "Completed step cannot contain an error."
                )

        if self.status == "failed":
            if not self.error:
                raise ValueError(
                    "Failed step must contain an error."
                )


@dataclass(frozen=True)
class ResearchExecutionResult:
    question: str
    steps: tuple[StepExecution, ...]
    completed_steps: int
    failed_steps: int

    def validate(self) -> None:
        if not self.question.strip():
            raise ValueError(
                "ResearchExecutionResult.question cannot be empty."
            )

        if not self.steps:
            raise ValueError(
                "ResearchExecutionResult must contain steps."
            )

        if self.completed_steps < 0:
            raise ValueError(
                "completed_steps cannot be negative."
            )

        if self.failed_steps < 0:
            raise ValueError(
                "failed_steps cannot be negative."
            )

        if (
            self.completed_steps + self.failed_steps
            != len(self.steps)
        ):
            raise ValueError(
                "Step counts do not match execution records."
            )

        for execution in self.steps:
            execution.validate()
