from research.provenance import (
    build_claim_trace,
    rank_claim_evidence,
)

from research.result import ResearchEvidence


def make_evidence(
    source_id: str,
    text: str,
    relevance: float = 0.0,
):
    return ResearchEvidence(
        source_id=source_id,
        source_url=f"https://example.com/{source_id}",
        text=text,
        relevance=relevance,
    )


def test_rank_claim_evidence_finds_candidate():
    evidence = [
        make_evidence(
            "source-1",
            "The system uses retrieval augmented generation "
            "with vector database search.",
            relevance=0.8,
        ),
        make_evidence(
            "source-2",
            "The project contains a frontend application.",
        ),
    ]

    matches = rank_claim_evidence(
        "The system uses retrieval augmented generation",
        evidence,
    )

    assert len(matches) == 1
    assert matches[0]["source_id"] == "source-1"
    assert matches[0]["overlap"] > 0


def test_rank_claim_evidence_returns_empty_when_missing():
    evidence = [
        make_evidence(
            "source-1",
            "The project contains a frontend application.",
        ),
    ]

    matches = rank_claim_evidence(
        "The system uses a vector database",
        evidence,
    )

    assert matches == []


def test_trace_marks_candidate_without_verifying_claim():
    evidence = [
        make_evidence(
            "source-1",
            "The service exposes a FastAPI API.",
        ),
    ]

    trace = build_claim_trace(
        "The service exposes a FastAPI API",
        evidence,
    )

    assert trace["status"] == (
        "candidate_evidence_found"
    )

    assert trace["verified"] is False
    assert trace["evidence"][0]["source_id"] == "source-1"


def test_trace_marks_insufficient_evidence():
    evidence = [
        make_evidence(
            "source-1",
            "The project contains documentation.",
        ),
    ]

    trace = build_claim_trace(
        "The system uses MCP tool calling",
        evidence,
    )

    assert trace["status"] == (
        "insufficient_evidence"
    )

    assert trace["verified"] is False
    assert trace["evidence"] == []


def test_empty_claim_rejected():
    evidence = [
        make_evidence(
            "source-1",
            "Some evidence.",
        ),
    ]

    try:
        rank_claim_evidence(
            "",
            evidence,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )
