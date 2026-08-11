import pytest

from research.profile import ProfileRecord


def make_record():
    return ProfileRecord(
        profile_id="example-profile",
        source_type="github_repository",
        source_url="https://example.com/repo",
        claim="Example technical evidence.",
        confidence="high",
        extracted={
            "ai_capabilities": {
                "rag": "true",
            }
        },
        retrieved_at="2026-08-11T00:00:00Z",
    )


def test_profile_record_validates():
    record = make_record()

    record.validate()


def test_profile_record_preserves_provenance():
    record = make_record()

    assert record.profile_id == "example-profile"
    assert record.source_type == "github_repository"
    assert record.source_url == "https://example.com/repo"
    assert record.claim == "Example technical evidence."


def test_profile_record_requires_extracted_data():
    record = ProfileRecord(
        profile_id="example-profile",
        source_type="github_repository",
        source_url="https://example.com/repo",
        claim="claim",
        confidence="high",
        extracted={},
        retrieved_at="2026-08-11T00:00:00Z",
    )

    with pytest.raises(ValueError):
        record.validate()
