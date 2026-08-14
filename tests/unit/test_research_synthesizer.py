from research.execution import (
    ResearchExecutionResult,
    StepExecution,
)
from research.result import (
    ResearchEvidence,
    ResearchResult,
)
from research.plan import ResearchStep
from research.synthesis import (
    ResearchSynthesis,
    SynthesisClaim,
)
from research.synthesizer import ResearchSynthesizer


class FakeProvider:
    def __init__(self, response):
        self.response = response
        self.prompt = None
        self.schema = None

    def generate_json(
        self,
        *,
        prompt,
        schema,
        performance=None,
    ):
        self.prompt = prompt
        self.schema = schema
        return self.response


def make_execution():
    step_a = ResearchStep(
        id="step-a",
        question="Find web evidence.",
        source_types=("web",),
        expected_evidence="Web evidence.",
        priority=1,
    )

    step_b = ResearchStep(
        id="step-b",
        question="Find GitHub evidence.",
        source_types=("github",),
        expected_evidence="Repository evidence.",
        priority=2,
    )

    result_a = ResearchResult(
        question="Find web evidence.",
        answer={"status": "ok"},
        evidence=(
            ResearchEvidence(
                source_id="web-1",
                source_url="https://example.com",
                text="Web evidence.",
            ),
        ),
        sources_considered=1,
        sources_collected=1,
    )

    result_b = ResearchResult(
        question="Find GitHub evidence.",
        answer={"status": "ok"},
        evidence=(
            ResearchEvidence(
                source_id="github-1",
                source_url="https://github.com/example/repo",
                text="Repository evidence.",
            ),
        ),
        sources_considered=1,
        sources_collected=1,
    )

    return ResearchExecutionResult(
        question="Research AI systems.",
        steps=(
            StepExecution(
                step=step_a,
                status="completed",
                attempts=1,
                result=result_a,
            ),
            StepExecution(
                step=step_b,
                status="completed",
                attempts=1,
                result=result_b,
            ),
        ),
        completed_steps=2,
        failed_steps=0,
    )


def test_synthesizer_builds_grounded_result():
    provider = FakeProvider(
        {
            "answer": "The evidence shows an AI system.",
            "claims": [
                {
                    "claim_id": "claim-1",
                    "text": "The system has documented AI-related implementation.",
                    "evidence_ids": [
                        "web-1",
                        "github-1",
                    ],
                }
            ],
        }
    )

    result = ResearchSynthesizer(
        provider=provider,
    ).synthesize(
        make_execution()
    )

    assert isinstance(result, ResearchSynthesis)
    assert result.answer.startswith("The evidence")
    assert result.sources_used == 2
    assert result.claims[0].support_status == "corroborated"


def test_synthesizer_marks_multiple_web_sources_as_corroborated():
    execution = make_execution()

    web_step = execution.steps[0]

    existing_result = web_step.result

    assert existing_result is not None

    second_web_evidence = ResearchEvidence(
        source_id="web-2",
        source_url="https://example.org",
        text="Independent web evidence.",
    )

    updated_result = ResearchResult(
        question=existing_result.question,
        answer=existing_result.answer,
        evidence=(
            *existing_result.evidence,
            second_web_evidence,
        ),
        sources_considered=2,
        sources_collected=2,
    )

    execution = ResearchExecutionResult(
        question=execution.question,
        steps=(
            StepExecution(
                step=web_step.step,
                status=web_step.status,
                attempts=web_step.attempts,
                result=updated_result,
            ),
            execution.steps[1],
        ),
        completed_steps=execution.completed_steps,
        failed_steps=execution.failed_steps,
    )

    provider = FakeProvider(
        {
            "answer": "The evidence shows an AI system.",
            "claims": [
                {
                    "claim_id": "claim-1",
                    "text": (
                        "The system has documented "
                        "AI-related implementation."
                    ),
                    "evidence_ids": [
                        "web-1",
                        "web-2",
                    ],
                },
            ],
        }
    )

    result = ResearchSynthesizer(
        provider=provider,
    ).synthesize(
        execution
    )

    assert result.claims[0].support_status == (
        "corroborated"
    )


def test_synthesizer_rejects_unknown_evidence():
    provider = FakeProvider(
        {
            "answer": "Answer.",
            "claims": [
                {
                    "claim_id": "claim-1",
                    "text": "Unsupported.",
                    "evidence_ids": [
                        "does-not-exist",
                    ],
                }
            ],
        }
    )

    try:
        ResearchSynthesizer(provider).synthesize(
            make_execution()
        )
    except ValueError as exc:
        assert "unknown evidence" in str(exc).lower()
    else:
        raise AssertionError(
            "Expected unknown evidence to fail."
        )


def test_synthesizer_rejects_empty_answer():
    provider = FakeProvider(
        {
            "answer": "",
            "claims": [],
        }
    )

    try:
        ResearchSynthesizer(provider).synthesize(
            make_execution()
        )
    except ValueError as exc:
        assert "answer" in str(exc).lower()
    else:
        raise AssertionError(
            "Expected empty answer to fail."
        )


def test_synthesizer_retries_after_meta_answer():
    class SequenceProvider:
        def __init__(self):
            self.responses = [
                {
                    "answer": (
                        "The user has provided a research request."
                    ),
                    "claims": [],
                },
                {
                    "answer": (
                        "The evidence describes an AI system."
                    ),
                    "claims": [
                        {
                            "claim_id": "claim-1",
                            "text": (
                                "The system has documented "
                                "AI-related implementation."
                            ),
                            "evidence_ids": [
                                "web-1",
                            ],
                        },
                    ],
                },
            ]
            self.calls = 0

        def generate_json(
            self,
            *,
            prompt,
            schema,
            performance=None,
        ):
            self.calls += 1
            return self.responses.pop(0)

    provider = SequenceProvider()

    result = ResearchSynthesizer(
        provider=provider,
        max_quality_retries=1,
    ).synthesize(
        make_execution()
    )

    assert provider.calls == 2
    assert result.answer.startswith(
        "The evidence"
    )


def test_synthesizer_stops_after_bounded_quality_retry():
    class SequenceProvider:
        def __init__(self):
            self.calls = 0

        def generate_json(
            self,
            *,
            prompt,
            schema,
            performance=None,
        ):
            self.calls += 1

            return {
                "answer": (
                    "The user has provided a research request."
                ),
                "claims": [],
            }

    provider = SequenceProvider()

    try:
        ResearchSynthesizer(
            provider=provider,
            max_quality_retries=1,
        ).synthesize(
            make_execution()
        )
    except ValueError as exc:
        assert "meta" in str(exc).lower()
    else:
        raise AssertionError(
            "Expected bounded quality retry to fail."
        )

    assert provider.calls == 2


def test_synthesizer_rejects_missing_evidence():
    provider = FakeProvider(
        {
            "answer": "Answer.",
            "claims": [],
        }
    )

    execution = ResearchExecutionResult(
        question="Research AI systems.",
        steps=(
            StepExecution(
                step=ResearchStep(
                    id="step-a",
                    question="No evidence.",
                    source_types=("web",),
                    expected_evidence="Evidence.",
                    priority=1,
                ),
                status="failed",
                attempts=1,
                error="No evidence.",
            ),
        ),
        completed_steps=0,
        failed_steps=1,
    )

    try:
        ResearchSynthesizer(provider).synthesize(
            execution
        )
    except ValueError as exc:
        assert "without evidence" in str(exc)
    else:
        raise AssertionError(
            "Expected no-evidence synthesis to fail."
        )


def test_synthesis_contract_rejects_unknown_claim_evidence():
    try:
        ResearchSynthesis(
            question="Question.",
            answer="Answer.",
            claims=(
                SynthesisClaim(
                    claim_id="claim-1",
                    text="Claim.",
                    evidence_ids=("missing",),
                    support_status="single_source",
                ),
            ),
            evidence_ids=("known",),
            sources_used=1,
        ).validate()
    except ValueError as exc:
        assert "unknown evidence" in str(exc).lower()
    else:
        raise AssertionError(
            "Expected contract validation to fail."
        )
