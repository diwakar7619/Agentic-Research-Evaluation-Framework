from dataclasses import dataclass

from research.execution import (
    ResearchExecutionResult,
    StepExecution,
)
from research.executor import ResearchExecutor
from research.plan import ResearchPlan, ResearchStep
from research.result import ResearchEvidence, ResearchResult
from research.task import ResearchTask


def make_task():
    return ResearchTask(
        name="phase14",
        question="Research AI systems.",
        source_types=("web", "github"),
        extraction_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
            },
        },
    )


def make_plan():
    return ResearchPlan(
        question="Research AI systems.",
        steps=(
            ResearchStep(
                id="step-1",
                question="Find primary evidence.",
                source_types=("web",),
                expected_evidence="Primary technical evidence.",
                priority=1,
            ),
            ResearchStep(
                id="step-2",
                question="Find independent evidence.",
                source_types=("github",),
                expected_evidence="Repository evidence.",
                priority=2,
            ),
        ),
    )


def make_result(question):
    return ResearchResult(
        question=question,
        answer={"status": "ok"},
        evidence=(
            ResearchEvidence(
                source_id="source-1",
                source_url="https://example.com",
                text="Evidence.",
            ),
        ),
        sources_considered=1,
        sources_collected=1,
    )


class FakeRunner:
    def __init__(self):
        self.tasks = []

    def run(self, task):
        self.tasks.append(task)
        return make_result(task.question)


def test_executor_runs_each_plan_step():
    runner = FakeRunner()

    executor = ResearchExecutor(
        runner=runner,
        max_attempts_per_step=1,
    )

    result = executor.run(
        make_task(),
        make_plan(),
    )

    assert isinstance(
        result,
        ResearchExecutionResult,
    )

    assert result.completed_steps == 2
    assert result.failed_steps == 0
    assert len(result.steps) == 2

    assert [
        task.question
        for task in runner.tasks
    ] == [
        "Find primary evidence.",
        "Find independent evidence.",
    ]


def test_executor_preserves_step_source_types():
    runner = FakeRunner()

    executor = ResearchExecutor(
        runner=runner,
        max_attempts_per_step=1,
    )

    executor.run(
        make_task(),
        make_plan(),
    )

    assert runner.tasks[0].source_types == ("web",)
    assert runner.tasks[1].source_types == ("github",)


class FlakyRunner:
    def __init__(self):
        self.calls = 0

    def run(self, task):
        self.calls += 1

        if self.calls == 1:
            raise RuntimeError("temporary failure")

        return make_result(task.question)


def test_executor_retries_failed_step_within_budget():
    runner = FlakyRunner()

    plan = ResearchPlan(
        question="Research AI systems.",
        steps=(
            ResearchStep(
                id="step-1",
                question="Retry this step.",
                source_types=("web",),
                expected_evidence="Evidence.",
                priority=1,
            ),
        ),
    )

    executor = ResearchExecutor(
        runner=runner,
        max_attempts_per_step=2,
    )

    result = executor.run(
        make_task(),
        plan,
    )

    assert result.completed_steps == 1
    assert result.failed_steps == 0
    assert result.steps[0].attempts == 2


class AlwaysFailRunner:
    def run(self, task):
        raise RuntimeError("permanent failure")


def test_executor_bounds_failure():
    executor = ResearchExecutor(
        runner=AlwaysFailRunner(),
        max_attempts_per_step=2,
    )

    result = executor.run(
        make_task(),
        ResearchPlan(
            question="Research AI systems.",
            steps=(
                ResearchStep(
                    id="step-1",
                    question="Fail this.",
                    source_types=("web",),
                    expected_evidence="Evidence.",
                    priority=1,
                ),
            ),
        ),
    )

    assert result.completed_steps == 0
    assert result.failed_steps == 1
    assert result.steps[0].attempts == 2
    assert "permanent failure" in result.steps[0].error


def test_executor_rejects_plan_for_different_question():
    executor = ResearchExecutor(
        runner=FakeRunner(),
    )

    mismatched = ResearchPlan(
        question="Different question.",
        steps=(
            ResearchStep(
                id="step-1",
                question="Something.",
                source_types=("web",),
                expected_evidence="Evidence.",
            ),
        ),
    )

    try:
        executor.run(
            make_task(),
            mismatched,
        )
    except ValueError as exc:
        assert "must match" in str(exc)
    else:
        raise AssertionError(
            "Expected mismatched plan to fail."
        )


def test_step_execution_validation():
    execution = StepExecution(
        step=make_plan().steps[0],
        status="completed",
        attempts=1,
        result=make_result(
            "Find primary evidence."
        ),
    )

    execution.validate()
