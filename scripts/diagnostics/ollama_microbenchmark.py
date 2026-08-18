import json
import time
import urllib.request

URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen3:4b"

tests = [
    {
        "name": "json_no_think",
        "body": {
            "model": MODEL,
            "prompt": 'Return exactly this JSON and nothing else: {"status":"ok"}',
            "format": "json",
            "stream": False,
            "think": False,
            "keep_alive": "10m",
            "options": {
                "num_predict": 128,
                "temperature": 0,
            },
        },
    },
    {
        "name": "json_think",
        "body": {
            "model": MODEL,
            "prompt": 'Return exactly this JSON and nothing else: {"status":"ok"}',
            "format": "json",
            "stream": False,
            "think": True,
            "keep_alive": "10m",
            "options": {
                "num_predict": 128,
                "temperature": 0,
            },
        },
    },
    {
        "name": "short_answer_no_think",
        "body": {
            "model": MODEL,
            "prompt": "In one short sentence, explain what RAG is.",
            "stream": False,
            "think": False,
            "keep_alive": "10m",
            "options": {
                "num_predict": 128,
                "temperature": 0,
            },
        },
    },
]

def call(body):
    raw = json.dumps(body).encode("utf-8")

    request = urllib.request.Request(
        URL,
        data=raw,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.perf_counter()

    with urllib.request.urlopen(
        request,
        timeout=180,
    ) as response:
        payload = json.loads(
            response.read().decode("utf-8")
        )

    wall = time.perf_counter() - started

    result = {
        "wall_seconds": round(wall, 4),
        "total_seconds": round(
            payload.get("total_duration", 0) / 1e9,
            4,
        ),
        "load_seconds": round(
            payload.get("load_duration", 0) / 1e9,
            4,
        ),
        "prompt_eval_seconds": round(
            payload.get("prompt_eval_duration", 0) / 1e9,
            4,
        ),
        "eval_seconds": round(
            payload.get("eval_duration", 0) / 1e9,
            4,
        ),
        "prompt_tokens": payload.get(
            "prompt_eval_count"
        ),
        "output_tokens": payload.get(
            "eval_count"
        ),
        "done_reason": payload.get(
            "done_reason"
        ),
    }

    if result["eval_seconds"]:
        result["output_tokens_per_second"] = round(
            result["output_tokens"]
            / result["eval_seconds"],
            3,
        )

    return result


for test in tests:
    print("")
    print("===== " + test["name"] + " =====")

    try:
        print(
            json.dumps(
                call(test["body"]),
                indent=2,
            )
        )
    except Exception as exc:
        print(
            json.dumps(
                {
                    "error": type(exc).__name__,
                    "message": str(exc),
                },
                indent=2,
            )
        )
