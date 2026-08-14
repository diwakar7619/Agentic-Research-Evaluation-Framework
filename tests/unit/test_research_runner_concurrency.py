import time

from research.result import ResearchEvidence
from research.runner import ResearchRunner
from research.source import SourceCandidate


class FakeDiscoverer:

    def __init__(self, count):
        self.count = count

    def discover(
        self,
        query,
        *,
        limit=10,
    ):
        return [
            SourceCandidate(
                source_id=f"web-{index}",
                source_type="web",
                title=f"Source {index}",
                url=f"https://example.com/{index}",
                metadata={},
            )
            for index in range(
                min(self.count, limit)
            )
        ]


class SlowCollector:

    def __init__(self, delay):
        self.delay = delay
        self.active = 0
        self.max_active = 0

    def collect(self, candidate):
        self.active += 1
        self.max_active = max(
            self.max_active,
            self.active,
        )

        try:
            time.sleep(self.delay)

            from research.source import CollectedSource

            return CollectedSource(
                source_id=candidate.source_id,
                source_type=candidate.source_type,
                title=candidate.title,
                url=candidate.url,
                content=(
                    "Test research evidence for "
                    f"{candidate.source_id}."
                ),
                metadata={},
            )
        finally:
            self.active -= 1


class FakeExtractor:

    def extract(
        self,
        *,
        question,
        evidence,
        schema,
    ):
        return {
            "answer": "Answer.",
            "claims": [],
        }


class FakeValidator:

    def validate(self, result):
        return result


def make_task(concurrency):
    from research.task import ResearchTask

    return ResearchTask(
        name="concurrency-test",
        question="Test research.",
        source_types=("web",),
        extraction_schema={},
        metadata={
            "max_sources": 5,
            "max_collection_concurrency": concurrency,
        },
    )


def test_source_collection_is_bounded():
    collector = SlowCollector(
        delay=0.05
    )

    runner = ResearchRunner(
        discoverer=FakeDiscoverer(5),
        collector=collector,
        extractor=FakeExtractor(),
        validator=FakeValidator(),
    )

    result = runner.run(
        make_task(2)
    )

    assert result.sources_collected == 5
    assert collector.max_active <= 2
    assert collector.max_active >= 2


def test_source_collection_preserves_discovery_order():
    collector = SlowCollector(
        delay=0.01
    )

    runner = ResearchRunner(
        discoverer=FakeDiscoverer(5),
        collector=collector,
        extractor=FakeExtractor(),
        validator=FakeValidator(),
    )

    result = runner.run(
        make_task(5)
    )

    assert [
        evidence.source_id
        for evidence in result.evidence
    ] == [
        "web-0",
        "web-1",
        "web-2",
        "web-3",
        "web-4",
    ]


def test_invalid_concurrency_is_rejected():
    collector = SlowCollector(
        delay=0.0
    )

    runner = ResearchRunner(
        discoverer=FakeDiscoverer(1),
        collector=collector,
        extractor=FakeExtractor(),
        validator=FakeValidator(),
    )

    try:
        runner.run(
            make_task(0)
        )
    except ValueError as exc:
        assert (
            "max_collection_concurrency"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected invalid concurrency to fail."
        )
