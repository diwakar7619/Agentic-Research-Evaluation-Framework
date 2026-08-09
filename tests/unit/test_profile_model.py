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


def test_profile_record_serializes_to_dict():
    profile = ProfileRecord.model_validate(
        {
            "identity": {
                "profile_id": "p-002",
                "name": "Serialization Test",
                "github_username": "serialization-test",
                "github_url": "https://github.com/serialization-test",
                "discovery_source": "manual",
                "research_status": "candidate",
            }
        }
    )

    data = profile.model_dump(mode="json")

    assert isinstance(data, dict)
    assert data["identity"]["github_username"] == "serialization-test"
    assert data["visibility"]["visibility_group"] == "unknown"
    assert data["metadata"]["schema_version"] == "1.0"


from datetime import datetime, timezone

from models.profile import EvidenceRecord, ProfileRecord


def test_evidence_record_validates():
    evidence = EvidenceRecord.model_validate(
        {
            "evidence_id": "e-001",
            "claim": "Project has a live demo",
            "source_url": "https://github.com/example/demo",
            "source_type": "github_readme",
            "evidence_text": "Live demo: https://demo.example.com",
            "confidence": "high",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    assert evidence.source_type.value == "github_readme"
    assert evidence.confidence.value == "high"


def test_profile_record_accepts_evidence():
    profile = ProfileRecord.model_validate(
        {
            "identity": {
                "profile_id": "p-003",
                "name": "Evidence Builder",
                "github_username": "evidence-builder",
                "github_url": "https://github.com/evidence-builder",
                "discovery_source": "manual",
                "research_status": "candidate",
            },
            "evidence": [
                {
                    "evidence_id": "e-001",
                    "claim": "Project has a live demo",
                    "source_url": "https://github.com/example/demo",
                    "source_type": "github_readme",
                    "evidence_text": "Live demo: https://demo.example.com",
                    "confidence": "high",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }
    )

    assert len(profile.evidence) == 1
    assert profile.evidence[0].claim == "Project has a live demo"
