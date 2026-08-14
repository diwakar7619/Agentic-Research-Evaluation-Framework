from research.ollama import OllamaProvider


def test_ollama_prompt_budget_is_enforced():
    provider = OllamaProvider(
        max_prompt_characters=1000,
    )

    try:
        provider.generate_json(
            prompt="x" * 1001,
            schema={
                "type": "object",
                "properties": {},
            },
        )
    except ValueError as exc:
        assert "Prompt exceeds safety budget" in str(exc)
        return

    raise AssertionError(
        "Oversized LLM prompts must be rejected before HTTP."
    )
