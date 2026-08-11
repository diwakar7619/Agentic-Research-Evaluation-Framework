from datetime import datetime, timezone

from collector.web import fetch_webpage
from models.profile import Confidence, EvidenceRecord, SourceType
from storage import save_evidence_record


URL = "https://github.com/rohitg00/ai-engineering-from-scratch"


text = fetch_webpage(URL)

if text is None:
    raise RuntimeError("No usable content extracted")


evidence = EvidenceRecord(
    evidence_id="rohitg00-ai-engineering-from-scratch-source",
    claim="The GitHub repository page contains publicly accessible project and AI-engineering information.",
    source_url=URL,
    source_type=SourceType.github_repository,
    evidence_text=text,
    confidence=Confidence.high,
    retrieved_at=datetime.now(timezone.utc),
)

path = save_evidence_record(evidence)

print(f"Evidence saved: {path}")
print(f"Evidence characters: {len(text)}")
