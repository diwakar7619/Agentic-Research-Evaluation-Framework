from __future__ import annotations

import re


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for",
    "from", "how", "in", "into", "is", "it", "of", "on", "or",
    "that", "the", "this", "to", "what", "which", "with", "why",
    "about", "current", "state", "provide", "using", "use",
    "need", "happens", "when", "can", "should", "does",
    "do", "will", "would", "could", "their", "they", "them",
    "find", "primary", "purpose", "project", "supplied",
}


def content_terms(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]{3,}", text.lower())
        if token not in _STOPWORDS
    }


def alignment_score(question: str, candidate: str) -> float:
    question_terms = content_terms(question)
    candidate_terms = content_terms(candidate)

    if not question_terms or not candidate_terms:
        return 0.0

    return len(question_terms & candidate_terms) / len(question_terms)


# Generic groups are intentionally weak signals.
_GENERIC_DOMAINS = {
    "ai": {
        "ai", "agent", "agents", "llm", "model", "models",
    },
    "software": {
        "code", "coding", "software", "program", "programming",
        "implementation", "repository", "github",
    },
    "data": {
        "data", "database", "sql", "storage", "dataset", "datasets",
    },
}


# These are strong topic signals. A strong candidate domain that is
# absent from the question is evidence of topic drift.
_STRONG_DOMAINS = {
    "rag_retrieval": {
        "rag", "retrieval", "retriever", "embedding", "embeddings",
        "vector", "vectors", "vectorstore", "vectorstores",
    },
    "web_research": {
        "web", "http", "url", "urls", "website", "websites",
        "crawler", "crawl", "scrape", "scraping", "browser",
        "source", "sources",
    },
    "performance": {
        "performance", "latency", "throughput", "scalability",
        "scale", "concurrency", "cache", "caching",
    },
    "payments": {
        "payment", "payments", "transaction", "transactions",
        "refund", "refunds", "rollback", "saga",
    },
    "email": {
        "email", "emails", "mail",
    },
    "crm": {
        "crm", "ticket", "tickets", "customer",
    },
    "observability": {
        "observability", "telemetry", "metrics", "tracing",
        "logging", "monitoring",
    },
    "health_fitness": {
        "health", "medical", "medicine", "clinical",
        "therapy", "therapeutic", "exercise", "exercises",
        "fitness", "workout", "stretching", "strength",
        "strengthening", "hip", "hips", "pelvic", "tilt",
        "physiotherapy", "physio",
    },
}


def _domain_hits(text: str, domains: dict[str, set[str]]) -> set[str]:
    text = text.lower()
    result: set[str] = set()

    for domain, terms in domains.items():
        for term in terms:
            if re.search(rf"\b{re.escape(term)}\b", text):
                result.add(domain)
                break

    return result


def _topic_domains(text: str) -> set[str]:
    return (
        _domain_hits(text, _GENERIC_DOMAINS)
        | _domain_hits(text, _STRONG_DOMAINS)
    )


def _strong_domains(text: str) -> set[str]:
    return _domain_hits(text, _STRONG_DOMAINS)


def require_alignment(
    question: str,
    candidate: str,
    *,
    min_shared_terms: int = 2,
    min_score: float = 0.12,
) -> None:
    """
    Deterministic topic-alignment guard.

    Rules:

    1. Strong domains are meaningful topic signals.
    2. If both sides expose strong domains, at least one domain
       must overlap.
    3. A strong candidate domain cannot appear from nowhere when
       the question has no strong domain.
    4. Generic AI/software/data vocabulary cannot establish
       relevance by itself when the question has a strong topic.
    5. For ordinary cases with no strong domain, retain lexical
       alignment requirements so planner recall is preserved.
    """

    question_domains = _topic_domains(question)
    candidate_domains = _topic_domains(candidate)

    question_strong = _strong_domains(question)
    candidate_strong = _strong_domains(candidate)

    shared = content_terms(question) & content_terms(candidate)
    score = alignment_score(
        question,
        candidate,
    )

    # --------------------------------------------------------
    # Case 1:
    # Candidate introduces a strong domain while the question
    # has no strong domain.
    #
    # Example:
    #   question = generic research
    #   candidate = medical / payments / email
    #
    # That is unexplained topic drift.
    # --------------------------------------------------------

    if not question_strong and candidate_strong:

        raise ValueError(
            "Semantic alignment failure: "
            f"question={question!r}; "
            f"candidate={candidate!r}; "
            f"question_domains={sorted(question_domains)}; "
            f"candidate_domains={sorted(candidate_domains)}; "
            f"unexpected_strong_domains="
            f"{sorted(candidate_strong)}"
        )

    # --------------------------------------------------------
    # Case 2:
    # Both sides have strong domains, but none overlap.
    # --------------------------------------------------------

    if question_strong and candidate_strong:

        overlap = (
            question_strong
            & candidate_strong
        )

        if not overlap:

            raise ValueError(
                "Semantic alignment failure: "
                f"question={question!r}; "
                f"candidate={candidate!r}; "
                f"question_domains="
                f"{sorted(question_domains)}; "
                f"candidate_domains="
                f"{sorted(candidate_domains)}; "
                f"unexpected_strong_domains="
                f"{sorted(candidate_strong - question_strong)}"
            )

        # Shared strong domain establishes the topic.
        return

    # --------------------------------------------------------
    # Case 3:
    # The question has a strong domain, but the candidate only
    # contains generic AI/software/data vocabulary.
    #
    # Generic "AI" alone must not rescue unrelated material.
    # --------------------------------------------------------

    if question_strong and not candidate_strong:

        generic_only = bool(
            candidate_domains
            & _GENERIC_DOMAINS.keys()
        )

        # Generic AI/software/data vocabulary is not enough
        # to establish relevance for a strongly scoped question.
        # Use the function's configured alignment contract rather
        # than an unexplained second threshold.
        if generic_only:

            if (
                len(shared) < min_shared_terms
                or score < min_score
            ):

                raise ValueError(
                    "Semantic alignment failure: "
                    f"question={question!r}; "
                    f"candidate={candidate!r}; "
                    f"shared_terms={sorted(shared)}; "
                    f"score={score:.3f}; "
                    "generic-domain overlap is insufficient"
                )

            return

        # Candidate has no conflicting strong domain and is not
        # merely generic AI/software/data material. Require the
        # normal lexical alignment contract.
        if (
            len(shared) >= min_shared_terms
            and score >= min_score
        ):
            return

        raise ValueError(
            "Semantic alignment failure: "
            f"question={question!r}; "
            f"candidate={candidate!r}; "
            f"shared_terms={sorted(shared)}; "
            f"score={score:.3f}"
        )

    # Case 4:
    # Neither side has a strong domain.
    #
    # Preserve the original lexical guard.
    # --------------------------------------------------------

    if (
        len(shared) < min_shared_terms
        or score < min_score
    ):

        raise ValueError(
            "Semantic alignment failure: "
            f"question={question!r}; "
            f"candidate={candidate!r}; "
            f"shared_terms={sorted(shared)}; "
            f"score={score:.3f}"
        )
