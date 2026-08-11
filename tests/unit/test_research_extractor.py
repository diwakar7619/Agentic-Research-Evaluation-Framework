from research.extractor import extract_profile
from research.tasks.ai_engineering import AI_ENGINEERING_PROFILE_RESEARCH


def test_extract_profile_uses_task_schema(monkeypatch):
    captured = {}

    def fake_extract_json(prompt, *, response_schema=None):
        captured["prompt"] = prompt
        captured["schema"] = response_schema

        return {
            "ai_capabilities": {
                "llm_application": "true",
                "rag": "unknown",
                "embeddings": "unknown",
                "vector_database": "unknown",
                "agents": "unknown",
                "tool_calling": "unknown",
                "mcp": "unknown",
            },
            "engineering_signals": {
                "testing": "unknown",
                "ci_cd": "unknown",
                "docker": "unknown",
                "api_service": "unknown",
                "documentation": "true",
            },
        }

    monkeypatch.setattr(
        "research.extractor.extract_json",
        fake_extract_json,
    )

    evidence = {
        "evidence_id": "profile-1",
        "source_type": "github_repository",
        "source_url": "https://example.com/repo",
        "claim": "Technical evidence",
        "confidence": "high",
        "evidence_text": "Uses an LLM and provides documentation.",
        "retrieved_at": "2026-08-11T00:00:00Z",
    }

    record = extract_profile(
        AI_ENGINEERING_PROFILE_RESEARCH,
        evidence,
    )

    assert record.profile_id == "profile-1"
    assert record.source_type == "github_repository"
    assert record.extracted["ai_capabilities"]["llm_application"] == "true"
    assert captured["schema"] is AI_ENGINEERING_PROFILE_RESEARCH.extraction_schema
    assert "Uses an LLM" in captured["prompt"]


def test_extract_profile_rejects_empty_evidence():
    evidence = {
        "evidence_id": "profile-1",
        "source_type": "github_repository",
        "source_url": "https://example.com/repo",
        "claim": "claim",
        "confidence": "high",
        "evidence_text": "",
        "retrieved_at": "2026-08-11T00:00:00Z",
    }

    try:
        extract_profile(
            AI_ENGINEERING_PROFILE_RESEARCH,
            evidence,
        )
    except ValueError as exc:
        assert "evidence_text" in str(exc)
    else:
        raise AssertionError("Expected empty evidence to fail.")
