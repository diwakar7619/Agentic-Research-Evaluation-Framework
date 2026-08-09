from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from models.profile import ProfileRecord


def main() -> None:
    profile = ProfileRecord.model_validate(
        {
            "identity": {
                "profile_id": "demo-001",
                "name": "Demo",
                "github_username": "demo",
                "github_url": "https://github.com/demo",
                "discovery_source": "manual",
            }
        }
    )
    print(json.dumps(profile.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
