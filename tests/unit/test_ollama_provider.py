from research.ollama import OllamaProvider


def test_ollama_provider_defaults_are_bounded():
    provider = OllamaProvider()

    assert provider.model == "qwen3:4b"
    assert provider.timeout_seconds == 120.0
    assert provider.max_output_tokens == 768


def test_ollama_provider_rejects_invalid_limits():
    try:
        OllamaProvider(timeout_seconds=0)
    except ValueError as exc:
        assert "timeout_seconds" in str(exc)
    else:
        raise AssertionError("Expected invalid timeout to fail.")

    try:
        OllamaProvider(max_output_tokens=0)
    except ValueError as exc:
        assert "max_output_tokens" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid output limit to fail."
        )
