from research.evidence_audit import audit_claim
from research.result import ResearchEvidence


def make(
    source_id,
    text,
):
    return ResearchEvidence(
        source_id=source_id,
        source_url=f"https://example.com/{source_id}",
        text=text,
        relevance=0.8,
    )


def test_generic_words_do_not_create_support():

    result = audit_claim(
        "The service uses MCP",
        [
            make(
                "source-a",
                "The service uses FastAPI.",
            )
        ],
    )

    assert result["support"] == "insufficient"


def test_distinctive_single_term_can_match():

    result = audit_claim(
        "The service uses MCP",
        [
            make(
                "source-a",
                "The architecture exposes MCP tools.",
            )
        ],
    )

    assert result["support"] == "single_source"


def test_same_source_is_not_corroboration():

    result = audit_claim(
        "The service uses FastAPI",
        [
            make(
                "source-a",
                "The service uses FastAPI.",
            ),
            make(
                "source-a",
                "FastAPI powers the API.",
            ),
        ],
    )

    assert result["support"] == "single_source"


def test_two_sources_are_corroborated():

    result = audit_claim(
        "The service uses FastAPI",
        [
            make(
                "source-a",
                "The service uses FastAPI.",
            ),
            make(
                "source-b",
                "FastAPI powers the API.",
            ),
        ],
    )

    assert result["support"] == "corroborated"


def test_verification_is_never_claimed():

    result = audit_claim(
        "The service uses FastAPI",
        [
            make(
                "source-a",
                "The service uses FastAPI.",
            ),
        ],
    )

    assert result["verified"] is False
