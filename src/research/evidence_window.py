from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Sequence


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for",
    "from", "how", "in", "into", "is", "it", "of", "on", "or",
    "that", "the", "this", "to", "what", "which", "with", "why",
    "about", "current", "state", "using", "use", "need",
    "can", "should", "does", "do", "will", "would", "could",
    "their", "they", "them", "these", "those",
}


def _terms(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]{3,}", text.lower())
        if token not in _STOPWORDS
    }


def _chunks(
    text: str,
    *,
    chunk_size: int,
) -> list[str]:
    text = text.strip()

    if not text:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) <= chunk_size:
            candidate = (
                f"{current}\n\n{paragraph}"
                if current
                else paragraph
            )

            if len(candidate) <= chunk_size:
                current = candidate
                continue

        if current:
            chunks.append(current)
            current = ""

        if len(paragraph) <= chunk_size:
            current = paragraph
            continue

        # Long paragraph fallback.
        for start in range(0, len(paragraph), chunk_size):
            chunks.append(
                paragraph[start:start + chunk_size]
            )

    if current:
        chunks.append(current)

    return chunks


def _score(question_terms: set[str], text: str) -> float:
    if not question_terms:
        return 0.0

    candidate_terms = _terms(text)

    if not candidate_terms:
        return 0.0

    overlap = question_terms & candidate_terms

    return len(overlap) / len(question_terms)


@dataclass(frozen=True)
class EvidenceWindow:
    source_id: str
    source_url: str
    text: str


def select_evidence_windows(
    question: str,
    evidence: Sequence[object],
    *,
    max_total_chars: int = 12_000,
    max_per_source_chars: int = 2_500,
    chunk_size: int = 900,
) -> tuple[EvidenceWindow, ...]:
    """
    Deterministically reduce large source documents before LLM extraction.

    Guarantees:
    - no source contributes more than max_per_source_chars
    - total selected text never exceeds max_total_chars
    - source order remains deterministic
    - relevant chunks are preferred
    - empty sources are ignored
    """

    if max_total_chars < 1:
        raise ValueError("max_total_chars must be positive.")

    if max_per_source_chars < 1:
        raise ValueError(
            "max_per_source_chars must be positive."
        )

    if chunk_size < 1:
        raise ValueError("chunk_size must be positive.")

    question_terms = _terms(question)

    windows: list[EvidenceWindow] = []
    total_chars = 0

    for item in evidence:
        source_id = str(
            getattr(item, "source_id", "")
        )

        source_url = str(
            getattr(item, "source_url", "")
        )

        text = str(
            getattr(item, "text", "")
        ).strip()

        if not text:
            continue

        chunks = _chunks(
            text,
            chunk_size=chunk_size,
        )

        if not chunks:
            continue

        ranked = sorted(
            enumerate(chunks),
            key=lambda pair: (
                -_score(question_terms, pair[1]),
                pair[0],
            ),
        )

        selected_parts: list[str] = []
        source_chars = 0

        for _, chunk in ranked:
            remaining_source = (
                max_per_source_chars - source_chars
            )

            if remaining_source <= 0:
                break

            remaining_total = (
                max_total_chars - total_chars
            )

            if remaining_total <= 0:
                break

            budget = min(
                remaining_source,
                remaining_total,
            )

            if len(chunk) > budget:
                chunk = chunk[:budget]

            chunk = chunk.strip()

            if not chunk:
                continue

            selected_parts.append(chunk)
            source_chars += len(chunk)
            total_chars += len(chunk)

            if source_chars >= max_per_source_chars:
                break

            if total_chars >= max_total_chars:
                break

        if selected_parts:
            windows.append(
                EvidenceWindow(
                    source_id=source_id,
                    source_url=source_url,
                    text="\n\n".join(selected_parts),
                )
            )

        if total_chars >= max_total_chars:
            break

    return tuple(windows)
