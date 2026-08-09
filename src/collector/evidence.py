from datetime import datetime, timezone

from models.profile import Confidence, EvidenceRecord, SourceType


def create_evidence(
    *,
    evidence_id: str,
    claim: str,
    source_url: str,
    source_type: SourceType,
    evidence_text: str,
    confidence: Confidence,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        claim=claim,
        source_url=source_url,
        source_type=source_type,
        evidence_text=evidence_text,
        confidence=confidence,
        retrieved_at=datetime.now(timezone.utc),
    )
