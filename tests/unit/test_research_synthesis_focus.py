from research.synthesizer import ResearchSynthesizer


class CaptureProvider:

    def __init__(self):
        self.prompt = None
        self.schema = None

    def generate_json(self, *, prompt, schema):
        self.prompt = prompt
        self.schema = schema

        return {
            "answer": "Qdrant answer.",
            "claims": [
                {
                    "claim_id": "claim-1",
                    "text": "Qdrant is a vector database.",
                    "evidence_ids": ["web-1"],
                }
            ],
        }


def test_synthesis_prompt_requires_direct_question_focus():
    from research.execution import (
        ResearchExecutionResult,
        StepExecution,
    )
    from research.plan import ResearchStep
    from research.result import (
        ResearchEvidence,
        ResearchResult,
    )

    step = ResearchStep(
        id="focus-test",
        question="What is Qdrant?",
        source_types=("web",),
        expected_evidence="Definition.",
        priority=1,
    )

    result = ResearchResult(
        question=step.question,
        answer={"status": "collected"},
        evidence=(
            ResearchEvidence(
                source_id="web-1",
                source_url="https://example.com",
                text="Qdrant is a vector database.",
            ),
        ),
        sources_considered=1,
        sources_collected=1,
    )

    execution = ResearchExecutionResult(
        question=step.question,
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

    provider = CaptureProvider()

    ResearchSynthesizer(
        provider=provider
    ).synthesize(execution)

    assert provider.prompt is not None

    assert (
        "Answer the research question directly"
        in provider.prompt
    )

    assert (
        "Focus the answer on what the question actually asks"
        in provider.prompt
    )

    assert (
        "Do not answer a broader or different question"
        in provider.prompt
    )

    assert (
        "Do not introduce tangential comparisons"
        in provider.prompt
    )
