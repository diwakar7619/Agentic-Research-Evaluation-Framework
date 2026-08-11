import json
from pathlib import Path

from research.extractor import extract_profile
from research.tasks.ai_engineering import AI_ENGINEERING_PROFILE_RESEARCH


EVIDENCE_PATH = Path(
    "data/evidence/rohitg00-ai-engineering-from-scratch-source.json"
)


evidence = json.loads(
    EVIDENCE_PATH.read_text(encoding="utf-8")
)

record = extract_profile(
    AI_ENGINEERING_PROFILE_RESEARCH,
    evidence,
)

print(json.dumps(
    {
        "profile_id": record.profile_id,
        "source_type": record.source_type,
        "source_url": record.source_url,
        "claim": record.claim,
        "confidence": record.confidence,
        "extracted": record.extracted,
        "retrieved_at": record.retrieved_at,
    },
    indent=2,
))

print("\nPROFILE RECORD: PASS")
