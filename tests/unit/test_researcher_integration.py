from __future__ import annotations

from dataclasses import dataclass

from research.execution import (
    ResearchExecutionResult,
)
from research.researcher import (
    ResearchReport,
    Researcher,
)
from research.result import (
    ResearchEvidence,
    ResearchResult,
)


class FakePlanner:
    def __init__(self):
        self.performance = None

    def plan(
        self,
        task,
        *,
        performance=None,
    ):
        self.performance = performance
        return "fake-plan"


class FakeRunner:
    """
    Minimal implementation of the runner contract.

    The real production runner is injected separately.
    """

    def run(self, question):
        return ResearchResult(
            question=question,
            answer={"status": "collected"},
            evidence=(
                ResearchEvidence(
                    source_id="integration-source",
                    source_url="https://example.com",
                    text="Integration evidence.",
                ),
            ),
            sources_considered=1,
            sources_collected=1,
        )


class FakeExecutor:
    def __init__(self):
        self.runner = FakeRunner()

    def run(self, task, plan):
        from research.execution import StepExecution
        from research.plan import ResearchStep

        step = ResearchStep(
            id="integration-step",
            question=task.question,
            source_types=("web",),
            expected_evidence="Integration evidence.",
            priority=1,
        )

        result = self.runner.run(
            task.question
        )

        return ResearchExecutionResult(
            question=task.question,
            steps=(
                StepExecution(
                    step=step,
                    status="completed",
                    attempts=1,
                    result=result,
                ),
            ),
            completed_steps=1,
            failed_steps=0,
        )


class FakeSynthesizer:
    def __init__(self):
        self.performance = None

    def synthesize(
        self,
        execution,
        *,
        performance=None,
    ):
        self.performance = performance
        from research.synthesis import (
            ResearchSynthesis,
            SynthesisClaim,
        )

        return ResearchSynthesis(
            question=execution.question,
            answer="Integration succeeded.",
            claims=(
                SynthesisClaim(
                    claim_id="integration-claim",
                    text="Integration succeeded.",
                    evidence_ids=("integration-source",),
                    support_status="single_source",
                ),
            ),
            evidence_ids=("integration-source",),
            sources_used=1,
        )


class FakeStore:
    def __init__(self):
        self.calls = []

    def save_run(self, *args):
        self.calls.append(("run", args))

    def save_source(self, *args):
        self.calls.append(("source", args))

    def save_evidence(self, *args):
        self.calls.append(("evidence", args))

    def save_claim(self, *args):
        self.calls.append(("claim", args))

    def save_synthesis(self, *args):
        self.calls.append(("synthesis", args))


def test_unified_researcher_pipeline():
    from research.task import ResearchTask

    task = ResearchTask(
        name="integration-test",
        question="Does the unified research boundary work?",
        source_types=("web",),
        extraction_schema={
            "status": "string",
        },
    )

    store = FakeStore()

    planner = FakePlanner()
    synthesizer = FakeSynthesizer()

    researcher = Researcher(
        planner=planner,
        executor=FakeExecutor(),
        synthesizer=synthesizer,
        store=store,
    )

    report = researcher.run(
        task,
        run_id="integration-run",
    )

    assert isinstance(
        report,
        ResearchReport,
    )

    assert report.run_id == "integration-run"
    assert report.question == task.question

    assert report.execution.completed_steps == 1

    assert planner.performance is not None
    assert synthesizer.performance is planner.performance

    assert report.synthesis.answer == (
        "Integration succeeded."
    )

    operations = [
        item[0]
        for item in store.calls
    ]

    assert operations == [
        "run",
        "source",
        "evidence",
        "claim",
        "synthesis",
    ]
