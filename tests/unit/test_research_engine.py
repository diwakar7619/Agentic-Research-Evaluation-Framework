from research.memory import (
    InMemoryCollector,
    InMemoryDiscoverer,
)
from research.result import ResearchResult
from research.runner import ResearchRunner
from research.source import SourceCandidate
from research.task import ResearchTask
from research.validator import ResearchValidator


class StubExtractor:

    def extract(
        self,
        *,
        question,
        evidence,
        schema,
    ):
        return {
            "status": "extracted",
            "question": question,
            "evidence_count": len(evidence),
        }


def make_task(
    source_types=("web",),
):

    return ResearchTask(
        name="generic_research",
        question="Research AI systems.",
        source_types=source_types,
        extraction_schema={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                }
            },
        },
    )


def make_runner():

    candidate = SourceCandidate(
        source_id="source-1",
        source_type="web",
        title="Example",
        url="https://example.com",
        metadata={},
    )

    return ResearchRunner(
        discoverer=InMemoryDiscoverer(
            [candidate]
        ),
        collector=InMemoryCollector(
            {
                "source-1":
                    "Evidence about AI systems."
            }
        ),
        extractor=StubExtractor(),
        validator=ResearchValidator(),
    )


def test_generic_task_contract():

    task = make_task()

    task.validate()

    assert task.name == "generic_research"
    assert task.question
    assert task.supports_source("web")


def test_generic_runner_produces_result():

    result = make_runner().run(
        make_task()
    )

    assert isinstance(
        result,
        ResearchResult,
    )

    assert result.sources_considered == 1
    assert result.sources_collected == 1
    assert len(result.evidence) == 1
    assert result.answer["status"] == "extracted"


import pytest


def test_runner_rejects_when_no_allowed_sources_are_collected():

    with pytest.raises(
        ValueError,
        match="No sources were collected",
    ):
        make_runner().run(
            make_task(
                source_types=("github",)
            )
        )


def test_runner_supports_non_github_research():

    task = make_task(
        source_types=("web",)
    )

    result = make_runner().run(task)

    assert result.sources_collected == 1


def test_runner_supports_max_sources_metadata():

    task = make_task()

    task.metadata["max_sources"] = 1

    result = make_runner().run(task)

    assert result.sources_considered == 1
