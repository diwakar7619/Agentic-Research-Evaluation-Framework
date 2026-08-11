from typing import Any

from extraction.qwen import extract_json
from research.profile import ProfileRecord
from research.task import ResearchTask


def _build_prompt(task: ResearchTask, evidence_text: str) -> str:
    return f"""
You are an evidence-based research extraction system.

Research question:
{task.question}

Analyze ONLY the supplied evidence.

Return ONLY the JSON object required by the supplied schema.

Rules:
- Use only the supplied evidence.
- Do not use outside knowledge.
- Do not guess.
- Use "unknown" when evidence is insufficient.
- Do not add fields.
- Do not return explanations.

Evidence:
{evidence_text}
"""


def extract_profile(
    task: ResearchTask,
    evidence: dict[str, Any],
    *,
    max_evidence_chars: int = 18000,
) -> ProfileRecord:
    """
    Extract one profile from one evidence record.

    The research task controls the question, source scope and schema.
    """

    task.validate()

    evidence_text = str(evidence.get("evidence_text", ""))

    if not evidence_text.strip():
        raise ValueError("Evidence record contains no evidence_text.")

    bounded_evidence = evidence_text[:max_evidence_chars]

    prompt = _build_prompt(task, bounded_evidence)

    extracted = extract_json(
        prompt,
        response_schema=task.extraction_schema,
    )

    record = ProfileRecord(
        profile_id=str(
            evidence.get("evidence_id", "")
        ),
        source_type=str(
            evidence.get("source_type", "")
        ),
        source_url=str(
            evidence.get("source_url", "")
        ),
        claim=str(
            evidence.get("claim", "")
        ),
        confidence=str(
            evidence.get("confidence", "")
        ),
        extracted=extracted,
        retrieved_at=str(
            evidence.get("retrieved_at", "")
        ),
    )

    record.validate()

    return record
