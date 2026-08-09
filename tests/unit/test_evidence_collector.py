from models.profile import Confidence, SourceType

from collector.evidence import create_evidence


def test_create_evidence_returns_evidence_record():
    evidence = create_evidence(
        evidence_id="e-001",
        claim="Project uses Docker",
        source_url="https://github.com/example/project",
        source_type=SourceType.github_readme,
        evidence_text="The repository contains a Dockerfile.",
        confidence=Confidence.high,
    )

    assert evidence.evidence_id == "e-001"
    assert evidence.claim == "Project uses Docker"
    assert evidence.source_type == SourceType.github_readme
    assert evidence.confidence == Confidence.high
    assert evidence.retrieved_at is not None
