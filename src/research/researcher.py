from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .execution import ResearchExecutionResult
from .executor import ResearchExecutor
from .planner import ResearchPlanner
from .store import ResearchStore
from .synthesizer import ResearchSynthesizer
from .task import ResearchTask


@dataclass(frozen=True)
class ResearchReport:
    """Final result returned by the unified research boundary."""

    run_id: str
    question: str
    execution: ResearchExecutionResult
    synthesis: Any

    def validate(self) -> None:
        if not self.run_id.strip():
            raise ValueError("run_id must not be empty.")

        if not self.question.strip():
            raise ValueError("question must not be empty.")

        self.execution.validate()

        if self.synthesis is None:
            raise ValueError("synthesis must not be None.")


class Researcher:
    """Thin orchestration boundary for the research pipeline."""

    def __init__(
        self,
        *,
        planner: ResearchPlanner,
        executor: ResearchExecutor,
        synthesizer: ResearchSynthesizer,
        store: ResearchStore,
    ) -> None:
        self.planner = planner
        self.executor = executor
        self.synthesizer = synthesizer
        self.store = store

    def run(
        self,
        task: ResearchTask,
        *,
        run_id: str,
    ) -> ResearchReport:
        if not run_id.strip():
            raise ValueError("run_id must not be empty.")

        plan = self.planner.plan(task)

        execution = self.executor.run(
            task,
            plan,
        )

        synthesis = self.synthesizer.synthesize(
            execution,
        )

        self.store.save_run(
            run_id,
            task.question,
            execution,
        )

        for step_execution in execution.steps:
            if step_execution.result is None:
                continue

            for evidence in step_execution.result.evidence:
                self.store.save_source(
                    run_id,
                    evidence,
                )
                self.store.save_evidence(
                    run_id,
                    evidence,
                )

        for claim in synthesis.claims:
            self.store.save_claim(
                run_id,
                claim,
            )

        self.store.save_synthesis(
            run_id,
            synthesis,
        )

        report = ResearchReport(
            run_id=run_id,
            question=task.question,
            execution=execution,
            synthesis=synthesis,
        )

        report.validate()

        return report
