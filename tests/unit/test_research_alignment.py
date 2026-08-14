from research.alignment import alignment_score, require_alignment


def test_unrelated_research_question_fails_alignment():
    question = (
        "Research production-grade AI agent engineering, "
        "web research, retrieval, evidence and scalability."
    )

    unrelated = (
        "What happens when an AI agent needs to rollback "
        "payments and emails?"
    )

    try:
        require_alignment(question, unrelated)
    except ValueError:
        return

    raise AssertionError(
        "Unrelated research plan must fail semantic alignment."
    )


def test_relevant_subquestion_passes_alignment():
    question = (
        "Research production-grade AI agent engineering "
        "with reliable web research and scalable processing."
    )

    candidate = (
        "How can reliable web research pipelines scale "
        "source collection and processing?"
    )

    require_alignment(question, candidate)


def test_alignment_score_is_zero_for_unrelated_text():
    score = alignment_score(
        "production web research scalability",
        "payment rollback transactions",
    )

    assert score == 0.0
