import httpx
import pytest

from extraction.qwen import extract_json


class MockResponse:
    def __init__(self, payload, error=None):
        self.payload = payload
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error

    def json(self):
        return self.payload


def test_extract_json_parses_valid_response(monkeypatch):
    def mock_post(*args, **kwargs):
        return MockResponse(
            {
                "response": '{"name": "Example Builder", "rag": "true"}'
            }
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    result = extract_json("Extract profile information.")

    assert result["name"] == "Example Builder"
    assert result["rag"] == "true"


def test_extract_json_passes_response_schema(monkeypatch):
    captured = {}

    schema = {
        "type": "object",
        "properties": {
            "rag": {
                "type": "string",
                "enum": ["true", "false", "unknown"],
            }
        },
    }

    def mock_post(*args, **kwargs):
        captured["payload"] = kwargs["json"]

        return MockResponse(
            {
                "response": '{"rag": "true"}'
            }
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    result = extract_json(
        "Extract RAG capability.",
        response_schema=schema,
    )

    assert result["rag"] == "true"
    assert captured["payload"]["format"] == schema


def test_extract_json_raises_on_invalid_json(monkeypatch):
    def mock_post(*args, **kwargs):
        return MockResponse(
            {
                "response": '{"rag": "true"'
            }
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    with pytest.raises(ValueError, match="Qwen returned invalid JSON"):
        extract_json("Extract profile information.")


def test_extract_json_propagates_http_error(monkeypatch):
    error = httpx.HTTPStatusError(
        "server error",
        request=httpx.Request("POST", "http://test"),
        response=httpx.Response(500),
    )

    def mock_post(*args, **kwargs):
        return MockResponse({}, error=error)

    monkeypatch.setattr(httpx, "post", mock_post)

    with pytest.raises(httpx.HTTPStatusError):
        extract_json("Extract profile information.")
