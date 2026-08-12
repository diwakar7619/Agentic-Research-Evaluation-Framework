from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from research.execution import (
    ResearchExecutionResult,
    StepExecution,
)
from research.plan import ResearchPlan, ResearchStep
from research.task import ResearchTask


@dataclass
class ResearchExecutor:
    """
    Executes a validated ResearchPlan through the existing
    MultiSourceResearchRunner.

    This layer owns orchestration state only.
    Discovery, collection, extraction, validation and provenance
    remain owned by the existing research engine.
    """

    runner: Any
    max_attempts_per_step: int = 2
    min_sources_per_step: int = 1

    def __post_init__(self) -> None:
        if self.max_attempts_per_step < 1:
            raise ValueError(
                "max_attempts_per_step must be >= 1."
            )

        if self.min_sources_per_step < 1:
            raise ValueError(
                "min_sources_per_step must be >= 1."
            )

    def run(
        self,
        task: ResearchTask,
        plan: ResearchPlan,
    ) -> ResearchExecutionResult:
        task.validate()
        plan.validate()

        if plan.question != task.question:
            raise ValueError(
                "ResearchPlan.question must match ResearchTask.question."
            )

        executions: list[StepExecution] = []

        for step in plan.steps:
            execution = self._execute_step(
                parent_task=task,
                step=step,
            )

            executions.append(execution)

        completed = sum(
            execution.status == "completed"
            for execution in executions
        )

        failed = len(executions) - completed

        result = ResearchExecutionResult(
            question=task.question,
            steps=tuple(executions),
            completed_steps=completed,
            failed_steps=failed,
        )

        result.validate()

        return result

    def _execute_step(
        self,
        *,
        parent_task: ResearchTask,
        step: ResearchStep,
    ) -> StepExecution:
        step_task = self._build_step_task(
            parent_task,
            step,
        )

        last_error: str | None = None

        for attempt in range(
            1,
            self.max_attempts_per_step + 1,
        ):
            try:
                result = self.runner.run(step_task)

                self._validate_step_result(result)

                return StepExecution(
                    step=step,
                    status="completed",
                    attempts=attempt,
                    result=result,
                )

            except Exception as exc:
                last_error = (
                    f"{type(exc).__name__}: {exc}"
                )

        return StepExecution(
            step=step,
            status="failed",
            attempts=self.max_attempts_per_step,
            error=last_error or "Unknown execution failure.",
        )

    def _build_step_task(
        self,
        parent_task: ResearchTask,
        step: ResearchStep,
    ) -> ResearchTask:
        metadata = dict(parent_task.metadata)

        metadata["research_step_id"] = step.id
        metadata["expected_evidence"] = step.expected_evidence

        return ResearchTask(
            name=f"{parent_task.name}:{step.id}",
            question=step.question,
            source_types=step.source_types,
            extraction_schema=parent_task.extraction_schema,
            metadata=metadata,
        )

    def _validate_step_result(
        self,
        result,
    ) -> None:
        if result is None:
            raise ValueError(
                "Research runner returned no result."
            )

        if not result.evidence:
            raise ValueError(
                "Research step produced no evidence."
            )

        if result.sources_collected < self.min_sources_per_step:
            raise ValueError(
                "Research step did not collect enough sources."
            )

        if not result.answer:
            raise ValueError(
                "Research step produced an empty answer."
            )
