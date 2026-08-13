import pytest

from research.result import ResearchEvidence
from research.runner import ResearchRunner
from research.source import (
    CollectedSource,
    SourceCandidate,
)


class FakeDiscoverer:

    def __init__(self, candidates):
        self.candidates = candidates

    def discover(self, query, *, limit):
        return self.candidates


class FakeCollector:

    def __init__(self, successful_ids):
        self.successful_ids = set(successful_ids)

    def collect(self, candidate):

        if candidate.source_id not in self.successful_ids:
            raise RuntimeError(
                f"source unavailable: {candidate.source_id}"
            )

        return CollectedSource(
            source_id=candidate.source_id,
            source_type=candidate.source_type,
            title=candidate.title,
            url=candidate.url,
            content=f"Evidence from {candidate.source_id}",
            metadata={},
        )


class FakeExtractor:

    def extract(
        self,
        *,
        question,
        evidence,
        schema,
    ):
        return {
            "status": "ok",
            "evidence_count": len(evidence),
        }


class FakeValidator:

    def validate(self, result):
        return result


def candidate(source_id):
    return SourceCandidate(
        source_id=source_id,
        source_type="web",
        title=source_id,
        url=f"https://example.com/{source_id}",
        metadata={},
    )


def task():
    from research.task import ResearchTask

    return ResearchTask(
        name="failure-isolation",
        question="Can one inaccessible source be ignored?",
        source_types=("web",),
        extraction_schema={
            "status": "string",
        },
        metadata={
            "max_sources": 3,
        },
    )


def build_runner(
    candidates,
    successful_ids,
):
    return ResearchRunner(
        discoverer=FakeDiscoverer(candidates),
        collector=FakeCollector(successful_ids),
        extractor=FakeExtractor(),
        validator=FakeValidator(),
    )


def test_one_failed_source_does_not_fail_research():

    runner = build_runner(
        [
            candidate("blocked"),
            candidate("usable"),
        ],
        {"usable"},
    )

    result = runner.run(task())

    assert result.sources_considered == 2
    assert result.sources_collected == 1

    assert [
        evidence.source_id
        for evidence in result.evidence
    ] == ["usable"]


def test_multiple_failed_sources_are_skipped():

    runner = build_runner(
        [
            candidate("blocked-1"),
            candidate("blocked-2"),
            candidate("usable"),
        ],
        {"usable"},
    )

    result = runner.run(task())

    assert result.sources_considered == 3
    assert result.sources_collected == 1

    assert result.evidence == (
        ResearchEvidence(
            source_id="usable",
            source_url="https://example.com/usable",
            text="Evidence from usable",
        ),
    )


def test_all_sources_failed_returns_clear_error():

    runner = build_runner(
        [
            candidate("blocked-1"),
            candidate("blocked-2"),
        ],
        set(),
    )

    with pytest.raises(
        ValueError,
        match="No sources were collected",
    ):
        runner.run(task())
