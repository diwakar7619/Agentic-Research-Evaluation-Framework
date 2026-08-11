from datetime import datetime, timezone

from models.profile import Confidence, EvidenceRecord, SourceType
from storage import save_evidence_record


def test_save_evidence_record(tmp_path, monkeypatch):
    monkeypatch.setattr("storage.EVIDENCE_DIR", tmp_path)

    evidence = EvidenceRecord(
        evidence_id="test-evidence-001",
        claim="The source contains AI engineering project information.",
        source_url="https://github.com/example/project",
        source_type=SourceType.github_repository,
        evidence_text="AI engineering project information.",
        confidence=Confidence.high,
        retrieved_at=datetime.now(timezone.utc),
    )

    path = save_evidence_record(evidence)

    assert path.exists()
    assert path.suffix == ".json"

    saved = path.read_text(encoding="utf-8")

    assert "test-evidence-001" in saved
    assert "AI engineering project information." in saved
    assert "https://github.com/example/project" in saved
