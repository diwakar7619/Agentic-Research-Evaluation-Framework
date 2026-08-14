import pytest

from research.alignment import alignment_score, require_alignment


QUESTION = (
    "Research production-grade AI agent engineering including "
    "reliable web research, retrieval, evidence extraction, "
    "source validation, concurrency, caching, and scalable processing."
)


def test_relevant_ai_engineering_candidate_is_aligned():
    candidate = (
        "Production AI agent systems use retrieval, evidence extraction, "
        "source validation, concurrency, caching, and scalable processing."
    )

    require_alignment(QUESTION, candidate)


def test_unrelated_candidate_is_rejected():
    candidate = (
        "Anterior pelvic tilt can be improved with stretching and "
        "strength exercises for the hip flexors."
    )

    with pytest.raises(ValueError, match="Semantic alignment failure"):
        require_alignment(QUESTION, candidate)


def test_strong_topic_conflict_is_rejected():
    candidate = (
        "Payment transaction systems use refunds, rollback, and "
        "distributed transaction orchestration."
    )

    with pytest.raises(ValueError, match="Semantic alignment failure"):
        require_alignment(QUESTION, candidate)


def test_generic_ai_overlap_alone_does_not_prove_relevance():
    candidate = (
        "AI models are increasingly used in many unrelated consumer "
        "applications and entertainment systems."
    )

    assert alignment_score(QUESTION, candidate) >= 0.0

    # Generic AI vocabulary alone must not establish relevance.
    with pytest.raises(
        ValueError,
        match="Semantic alignment failure",
    ):
        require_alignment(QUESTION, candidate)


def test_generic_ai_candidate_with_sufficient_topic_overlap_is_allowed():
    candidate = (
        "AI agent engineering systems use retrieval, web research, "
        "evidence extraction, source validation, concurrency, "
        "caching, and scalable processing."
    )

    require_alignment(
        QUESTION,
        candidate,
    )

def test_retrieval_and_rag_candidate_is_aligned():
    candidate = (
        "RAG systems retrieve relevant documents and use vector "
        "embeddings to provide evidence to an AI agent."
    )

    require_alignment(QUESTION, candidate)

def test_relevant_web_research_candidate_is_aligned():
    candidate = (
        "Reliable web research systems validate sources, preserve "
        "provenance, and extract evidence from retrieved web pages."
    )

    require_alignment(QUESTION, candidate)


def test_relevant_performance_candidate_is_aligned():
    candidate = (
        "Production AI systems use concurrency, caching, throughput "
        "controls, and scalable processing."
    )

    require_alignment(QUESTION, candidate)


def test_payment_candidate_is_rejected():
    candidate = (
        "Payment systems process refunds, rollbacks, transactions, "
        "and distributed payment orchestration."
    )

    with pytest.raises(ValueError, match="Semantic alignment failure"):
        require_alignment(QUESTION, candidate)


def test_medical_candidate_is_rejected():
    candidate = (
        "Anterior pelvic tilt can be improved through hip-flexor "
        "stretching and strengthening exercises."
    )

    with pytest.raises(ValueError, match="Semantic alignment failure"):
        require_alignment(QUESTION, candidate)


def test_generic_ai_candidate_is_rejected_as_insufficient():
    candidate = (
        "AI models are increasingly used in consumer applications "
        "and entertainment products."
    )

    with pytest.raises(ValueError, match="Semantic alignment failure"):
        require_alignment(QUESTION, candidate)
