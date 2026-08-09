from datetime import datetime, timezone

from models.profile import ProfileRecord


def test_profile_record_validates_minimal_profile():
    profile = ProfileRecord.model_validate(
        {
            "identity": {
                "profile_id": "p-001",
                "name": "Example Builder",
                "github_username": "example-builder",
                "github_url": "https://github.com/example-builder",
                "discovery_source": "manual",
                "research_status": "candidate",
            }
        }
    )

    assert profile.identity.github_username == "example-builder"
    assert profile.visibility.visibility_group == "unknown"
    assert profile.metadata.schema_version == "1.0"
