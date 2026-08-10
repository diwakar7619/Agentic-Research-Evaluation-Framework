import json

import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:4b"


def extract_json(
    prompt: str,
    *,
    timeout: float = 180.0,
    response_schema: dict | None = None,
) -> dict:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": response_schema if response_schema else "json",
        "think": False,
        "options": {
            "num_predict": 1200,
            "temperature": 0,
        },
    }

    response = httpx.post(
        OLLAMA_URL,
        json=payload,
        timeout=timeout,
    )

    response.raise_for_status()

    result = response.json()
    raw_response = result["response"]

    try:
        return json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Qwen returned invalid JSON: {exc}\n"
            f"Raw response:\n{raw_response}"
        ) from exc
