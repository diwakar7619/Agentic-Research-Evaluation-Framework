from research.evidence_audit import (
    audit_claim,
    audit_claims,
)

from research.result import ResearchEvidence


def evidence(
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


def test_single_source_support_is_not_corroboration():
    result = audit_claim(
        "The service uses FastAPI",
        [
            evidence(
                "source-a",
                "The service uses FastAPI.",
            )
        ],
    )

    assert result["support"] == "single_source"
    assert result["source_count"] == 1
    assert result["verified"] is False


def test_two_independent_sources_are_corroborated():
    result = audit_claim(
        "The service uses FastAPI",
        [
            evidence(
                "source-a",
                "The service uses FastAPI.",
            ),
            evidence(
                "source-b",
                "FastAPI is used for the service API.",
            ),
        ],
    )

    assert result["support"] == "corroborated"
    assert result["source_count"] == 2
    assert result["verified"] is False


def test_duplicate_same_source_is_not_independent_support():
    result = audit_claim(
        "The service uses FastAPI",
        [
            evidence(
                "source-a",
                "The service uses FastAPI.",
            ),
            evidence(
                "source-a",
                "FastAPI is used for the service API.",
            ),
        ],
    )

    assert result["support"] == "single_source"
    assert result["source_count"] == 1


def test_missing_evidence_is_insufficient():
    result = audit_claim(
        "The service uses MCP",
        [
            evidence(
                "source-a",
                "The service uses FastAPI.",
            )
        ],
    )

    assert result["support"] == "insufficient"
    assert result["source_count"] == 0
    assert result["verified"] is False


def test_multiple_claim_audit_summary():
    result = audit_claims(
        [
            "The service uses FastAPI",
            "The service uses MCP",
        ],
        [
            evidence(
                "source-a",
                "The service uses FastAPI.",
            ),
            evidence(
                "source-b",
                "FastAPI powers the service API.",
            ),
        ],
    )

    assert result["summary"]["total_claims"] == 2
    assert result["summary"]["corroborated"] == 1
    assert result["summary"]["insufficient"] == 1
