import pytest

from research.result import ResearchEvidence
from research.runner import ResearchRunner
from research.source import CollectedSource, SourceCandidate


class FakeDiscoverer:

    def __init__(self, candidates):
        self.candidates = candidates

    def discover(self, query, *, limit):
        return self.candidates[:limit]


class FakeCollector:

    def collect(self, candidate):
        contents = {
            "relevant":
                "Production AI agent systems use retrieval, "
                "evidence extraction, source validation, "
                "concurrency, caching, and scalable processing.",

            "irrelevant":
                "Anterior pelvic tilt can be improved with "
                "stretching and hip flexor exercises.",
        }

        return CollectedSource(
            source_id=candidate.source_id,
            source_type=candidate.source_type,
            title=candidate.title,
            url=candidate.url,
            content=contents[candidate.source_id],
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


def make_candidate(source_id):
    return SourceCandidate(
        source_id=source_id,
        source_type="web",
        title=source_id,
        url=f"https://example.com/{source_id}",
        metadata={},
    )


def make_task():
    from research.task import ResearchTask

    return ResearchTask(
        name="relevance-contract",
        question=(
            "Research production-grade AI agent engineering "
            "including retrieval, evidence extraction, "
            "source validation, concurrency, caching, "
            "and scalable processing."
        ),
        source_types=("web",),
        extraction_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "evidence_count": {"type": "integer"},
            },
        },
        metadata={
            "max_sources": 2,
        },
    )


def make_runner():
    return ResearchRunner(
        discoverer=FakeDiscoverer(
            [
                make_candidate("relevant"),
                make_candidate("irrelevant"),
            ]
        ),
        collector=FakeCollector(),
        extractor=FakeExtractor(),
        validator=FakeValidator(),
    )


def test_relevance_is_recorded_on_evidence():

    result = make_runner().run(make_task())

    assert result.evidence

    for evidence in result.evidence:
        assert isinstance(
            evidence,
            ResearchEvidence,
        )

        assert 0.0 <= evidence.relevance <= 1.0


def test_irrelevant_source_does_not_reach_extractor():

    result = make_runner().run(make_task())

    evidence_ids = [
        evidence.source_id
        for evidence in result.evidence
    ]

    assert "relevant" in evidence_ids
    assert "irrelevant" not in evidence_ids
