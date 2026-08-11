from pathlib import Path
import hashlib

from models.profile import EvidenceRecord


RAW_DIR = Path("data/raw")
EVIDENCE_DIR = Path("data/evidence")


def _url_to_filename(url: str) -> str:
    """Create a stable filename from a URL."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def save_raw_content(url: str, content: str) -> Path:
    """Persist fetched source content locally."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{_url_to_filename(url)}.txt"
    path = RAW_DIR / filename

    path.write_text(content, encoding="utf-8")

    return path


def save_evidence_record(evidence: EvidenceRecord) -> Path:
    """Persist an EvidenceRecord as JSON."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    path = EVIDENCE_DIR / f"{evidence.evidence_id}.json"

    path.write_text(
        evidence.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return path
