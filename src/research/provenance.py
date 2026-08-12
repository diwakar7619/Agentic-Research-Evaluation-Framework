from __future__ import annotations

import re
from collections.abc import Iterable

from research.result import ResearchEvidence


_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "using",
    "with",
}


def _tokens(text: str) -> set[str]:
    words = re.findall(
        r"[a-z0-9_]+",
        text.lower(),
    )

    return {
        word
        for word in words
        if word not in _STOPWORDS
    }


def _overlap_score(
    claim: str,
    evidence_text: str,
) -> float:
    claim_tokens = _tokens(claim)
    evidence_tokens = _tokens(evidence_text)

    if not claim_tokens:
        return 0.0

    return len(
        claim_tokens & evidence_tokens
    ) / len(claim_tokens)


def rank_claim_evidence(
    claim: str,
    evidence: Iterable[ResearchEvidence],
    *,
    min_overlap: float = 0.20,
) -> list[dict]:
    """
    Rank evidence candidates for a claim.

    This is a deterministic retrieval/traceability signal.
    It does NOT establish that the claim is factually true.
    """

    if not claim.strip():
        raise ValueError(
            "claim cannot be empty."
        )

    if not 0.0 <= min_overlap <= 1.0:
        raise ValueError(
            "min_overlap must be between 0 and 1."
        )

    matches = []

    for item in evidence:

        score = _overlap_score(
            claim,
            item.text,
        )

        if score < min_overlap:
            continue

        matches.append(
            {
                "source_id": item.source_id,
                "source_url": item.source_url,
                "relevance": item.relevance,
                "overlap": round(score, 4),
                "evidence_text": item.text,
            }
        )

    matches.sort(
        key=lambda item: (
            -item["overlap"],
            -item["relevance"],
            item["source_id"],
        )
    )

    return matches


def build_claim_trace(
    claim: str,
    evidence: Iterable[ResearchEvidence],
    *,
    min_overlap: float = 0.20,
) -> dict:
    """
    Build an auditable claim-to-evidence trace.

    Status deliberately distinguishes candidate evidence
    from verified truth.
    """

    matches = rank_claim_evidence(
        claim,
        evidence,
        min_overlap=min_overlap,
    )

    if matches:
        status = "candidate_evidence_found"
    else:
        status = "insufficient_evidence"

    return {
        "claim": claim,
        "status": status,
        "verified": False,
        "evidence": matches,
    }
