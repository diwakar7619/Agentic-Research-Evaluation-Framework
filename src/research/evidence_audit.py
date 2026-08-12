from __future__ import annotations

from collections.abc import Iterable

from research.provenance import (
    _tokens,
    build_claim_trace,
)
from research.result import ResearchEvidence


_GENERIC_TERMS = {
    "application",
    "app",
    "project",
    "service",
    "system",
    "uses",
    "use",
    "used",
    "using",
    "supports",
    "support",
    "contains",
    "provides",
    "implements",
    "implementation",
    "technology",
    "tool",
    "tools",
    "api",
    "feature",
}


def _claim_specific_tokens(
    claim: str,
) -> set[str]:
    return (
        _tokens(claim)
        - _GENERIC_TERMS
    )


def _evidence_supports_claim(
    claim: str,
    evidence_text: str,
) -> bool:
    """
    Conservative lexical candidate check.

    This is NOT semantic verification.
    Generic words alone cannot establish support.
    """

    claim_terms = _claim_specific_tokens(
        claim
    )

    evidence_terms = _tokens(
        evidence_text
    )

    if not claim_terms:
        return False

    matched = (
        claim_terms
        & evidence_terms
    )

    # For multi-term claims require at least
    # half of the claim-specific terms.
    if len(claim_terms) > 1:
        return (
            len(matched) / len(claim_terms)
            >= 0.5
        )

    # Single distinctive term:
    return bool(matched)


def audit_claim(
    claim: str,
    evidence: Iterable[ResearchEvidence],
    *,
    min_sources: int = 2,
) -> dict:
    """
    Produce conservative claim/evidence assessment.

    Status values:

      insufficient
      single_source
      corroborated

    `verified` remains False because lexical matching
    cannot establish factual truth.
    """

    if not claim.strip():
        raise ValueError(
            "claim cannot be empty."
        )

    if min_sources < 1:
        raise ValueError(
            "min_sources must be at least 1."
        )

    evidence = tuple(evidence)

    matches = []

    for item in evidence:

        if not _evidence_supports_claim(
            claim,
            item.text,
        ):
            continue

        matches.append(
            {
                "source_id": item.source_id,
                "source_url": item.source_url,
                "relevance": item.relevance,
                "evidence_text": item.text,
            }
        )

    matches.sort(
        key=lambda item: (
            -item["relevance"],
            item["source_id"],
        )
    )

    source_ids = {
        item["source_id"]
        for item in matches
        if item["source_id"]
    }

    source_count = len(source_ids)

    if source_count == 0:
        support = "insufficient"

    elif source_count >= min_sources:
        support = "corroborated"

    else:
        support = "single_source"

    return {
        "claim": claim,
        "support": support,
        "source_count": source_count,
        "verified": False,
        "evidence": matches,
    }


def audit_claims(
    claims: Iterable[str],
    evidence: Iterable[ResearchEvidence],
    *,
    min_sources: int = 2,
) -> dict:
    evidence = tuple(evidence)

    results = [
        audit_claim(
            claim,
            evidence,
            min_sources=min_sources,
        )
        for claim in claims
    ]

    summary = {
        "total_claims": len(results),
        "insufficient": 0,
        "single_source": 0,
        "corroborated": 0,
    }

    for result in results:
        summary[
            result["support"]
        ] += 1

    return {
        "claims": results,
        "summary": summary,
    }
