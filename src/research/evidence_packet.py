from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Mapping, Any


DEFAULT_MAX_TOTAL_CHARS = 20_000
DEFAULT_MAX_PER_SOURCE_CHARS = 4_000


@dataclass(frozen=True)
class EvidencePacketItem:
    source_id: str
    source_url: str
    text: str


_STOPWORDS = {
    "the", "and", "for", "with", "from",
    "that", "this", "are", "was", "were",
    "about", "into", "have", "has", "had",
    "what", "which", "when", "where", "how",
    "why", "can", "could", "should",
    "would", "will", "using", "use",
}


def _field(item: object, name: str) -> str:
    if isinstance(item, Mapping):
        value = item.get(name, "")
    else:
        value = getattr(item, name, "")

    return str(value)


def _terms(text: str) -> set[str]:
    return {
        token
        for token in re.findall(
            r"[a-z0-9]{3,}",
            text.lower(),
        )
        if token not in _STOPWORDS
    }


def _relevance(question: str, text: str) -> int:
    question_terms = _terms(question)
    text_terms = _terms(text)

    if not question_terms or not text_terms:
        return 0

    return len(
        question_terms & text_terms
    )


def _best_snippets(
    question: str,
    text: str,
    *,
    max_chars: int,
) -> str:

    text = text.strip()

    if len(text) <= max_chars:
        return text

    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        text,
    )

    scored: list[tuple[int, int, str]] = []

    for index, sentence in enumerate(sentences):
        sentence = sentence.strip()

        if not sentence:
            continue

        scored.append(
            (
                _relevance(
                    question,
                    sentence,
                ),
                index,
                sentence,
            )
        )

    # Highest relevance first.
    # Original position breaks ties deterministically.
    scored.sort(
        key=lambda item: (
            -item[0],
            item[1],
        )
    )

    selected: list[tuple[int, str]] = []
    used = 0

    for score, index, sentence in scored:

        remaining = max_chars - used

        if remaining <= 0:
            break

        # Once we already have relevant material,
        # don't spend budget on completely unrelated sentences.
        if score == 0 and selected:
            continue

        piece = sentence[:remaining]

        if not piece:
            continue

        selected.append(
            (
                index,
                piece,
            )
        )

        used += len(piece)

    if not selected:
        return text[:max_chars]

    # Restore original document order.
    selected.sort(
        key=lambda item: item[0]
    )

    return " ".join(
        piece
        for _, piece in selected
    )[:max_chars]


def build_evidence_packet(
    question: str,
    evidence: Iterable[object],
    *,
    max_total_chars: int = DEFAULT_MAX_TOTAL_CHARS,
    max_per_source_chars: int = DEFAULT_MAX_PER_SOURCE_CHARS,
) -> tuple[EvidencePacketItem, ...]:

    if max_total_chars < 1:
        raise ValueError(
            "max_total_chars must be >= 1."
        )

    if max_per_source_chars < 1:
        raise ValueError(
            "max_per_source_chars must be >= 1."
        )

    # --------------------------------------------------------
    # Deduplicate source IDs.
    # --------------------------------------------------------

    unique: dict[str, object] = {}

    for item in evidence:

        source_id = _field(
            item,
            "source_id",
        )

        if not source_id:
            continue

        if source_id not in unique:
            unique[source_id] = item

    if not unique:
        return ()

    # --------------------------------------------------------
    # Rank sources by relevance.
    # --------------------------------------------------------

    ranked = list(
        enumerate(
            unique.values()
        )
    )

    ranked.sort(
        key=lambda pair: (
            -_relevance(
                question,
                _field(
                    pair[1],
                    "text",
                ),
            ),
            pair[0],
        )
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # The global budget applies to the FINAL rendered packet,
    # not merely to raw evidence text.
    #
    # Therefore metadata such as:
    #   EVIDENCE_ID
    #   SOURCE
    #   TEXT
    #   separators
    #
    # is charged against the same budget.
    # --------------------------------------------------------

    result: list[EvidencePacketItem] = []

    used_total = 0

    for _, item in ranked:

        source_id = _field(
            item,
            "source_id",
        )

        source_url = _field(
            item,
            "source_url",
        )

        raw_text = _field(
            item,
            "text",
        ).strip()

        if not raw_text:
            continue

        separator_cost = 2 if result else 0

        metadata_cost = len(
            f"EVIDENCE_ID: {source_id}\n"
            f"SOURCE: {source_url}\n"
            f"TEXT:\n"
        )

        available = (
            max_total_chars
            - used_total
            - separator_cost
            - metadata_cost
        )

        if available <= 0:
            break

        text_budget = min(
            max_per_source_chars,
            available,
        )

        snippet = _best_snippets(
            question,
            raw_text,
            max_chars=text_budget,
        )

        if not snippet:
            continue

        item_cost = (
            separator_cost
            + metadata_cost
            + len(snippet)
        )

        if used_total + item_cost > max_total_chars:
            # Defensive check. This should never happen because
            # available was calculated from the same representation.
            break

        result.append(
            EvidencePacketItem(
                source_id=source_id,
                source_url=source_url,
                text=snippet,
            )
        )

        used_total += item_cost

    return tuple(result)


def render_evidence_packet(
    packet: Iterable[EvidencePacketItem],
) -> str:

    return "\n\n".join(
        (
            f"EVIDENCE_ID: {item.source_id}\n"
            f"SOURCE: {item.source_url}\n"
            f"TEXT:\n{item.text}"
        )
        for item in packet
    )
