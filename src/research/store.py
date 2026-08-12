from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))

    if isinstance(value, dict):
        return {
            str(key): _jsonable(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]

    if isinstance(value, set):
        return sorted(_jsonable(item) for item in value)

    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump())

    if hasattr(value, "dict"):
        return _jsonable(value.dict())

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    return value


class ResearchStore:
    """
    Small SQLite persistence layer for research runs.

    The store deliberately persists JSON snapshots rather than
    coupling storage to individual domain implementations.

    This keeps persistence independent from planner, executor,
    crawler and synthesizer internals.
    """

    def __init__(
        self,
        path: str | Path = "data/research/research.db",
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    from contextlib import contextmanager

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(
            self.path,
        )
        connection.row_factory = sqlite3.Row

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS research_runs (
                    run_id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS research_sources (
                    run_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    canonical_url TEXT,
                    content_hash TEXT,
                    collected_at TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY(run_id, source_id),
                    FOREIGN KEY(run_id)
                        REFERENCES research_runs(run_id)
                );

                CREATE TABLE IF NOT EXISTS research_evidence (
                    run_id TEXT NOT NULL,
                    evidence_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY(run_id, evidence_id),
                    FOREIGN KEY(run_id)
                        REFERENCES research_runs(run_id)
                );

                CREATE TABLE IF NOT EXISTS research_claims (
                    run_id TEXT NOT NULL,
                    claim_id TEXT NOT NULL,
                    support_status TEXT,
                    evidence_ids TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY(run_id, claim_id),
                    FOREIGN KEY(run_id)
                        REFERENCES research_runs(run_id)
                );

                CREATE TABLE IF NOT EXISTS research_syntheses (
                    run_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    FOREIGN KEY(run_id)
                        REFERENCES research_runs(run_id)
                );

                CREATE INDEX IF NOT EXISTS
                    idx_sources_run
                    ON research_sources(run_id);

                CREATE INDEX IF NOT EXISTS
                    idx_evidence_run
                    ON research_evidence(run_id);

                CREATE INDEX IF NOT EXISTS
                    idx_claims_run
                    ON research_claims(run_id);
                """
            )

    def save_run(
        self,
        run_id: str,
        question: str,
        payload: Any,
    ) -> None:
        if not run_id:
            raise ValueError("run_id must not be empty.")

        if not question.strip():
            raise ValueError("question must not be empty.")

        encoded = json.dumps(
            _jsonable(payload),
            ensure_ascii=False,
        )

        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO research_runs
                (run_id, question, created_at, payload)
                VALUES (?, ?, ?, ?)
                """,
                (
                    run_id,
                    question,
                    _utc_now(),
                    encoded,
                ),
            )

    def save_source(
        self,
        run_id: str,
        source: Any,
    ) -> None:
        data = _jsonable(source)

        source_id = data.get("source_id")
        source_url = data.get("source_url")

        if not source_id:
            raise ValueError(
                "source must contain source_id."
            )

        if not source_url:
            raise ValueError(
                "source must contain source_url."
            )

        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO research_sources
                (
                    source_id,
                    run_id,
                    source_url,
                    canonical_url,
                    content_hash,
                    collected_at,
                    payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_id,
                    run_id,
                    source_url,
                    data.get("canonical_url"),
                    data.get("content_hash"),
                    _utc_now(),
                    json.dumps(
                        data,
                        ensure_ascii=False,
                    ),
                ),
            )

    def save_evidence(
        self,
        run_id: str,
        evidence: Any,
    ) -> None:
        data = _jsonable(evidence)

        evidence_id = (
            data.get("evidence_id")
            or data.get("source_id")
        )

        source_id = data.get(
            "source_id",
            evidence_id,
        )

        if not evidence_id:
            raise ValueError(
                "evidence must contain an evidence identifier."
            )

        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO research_evidence
                (
                    evidence_id,
                    run_id,
                    source_id,
                    created_at,
                    payload
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    evidence_id,
                    run_id,
                    source_id,
                    _utc_now(),
                    json.dumps(
                        data,
                        ensure_ascii=False,
                    ),
                ),
            )

    def save_claim(
        self,
        run_id: str,
        claim: Any,
    ) -> None:
        data = _jsonable(claim)

        claim_id = data.get("claim_id")
        evidence_ids = data.get(
            "evidence_ids",
            [],
        )

        if not claim_id:
            raise ValueError(
                "claim must contain claim_id."
            )

        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO research_claims
                (
                    claim_id,
                    run_id,
                    support_status,
                    evidence_ids,
                    payload
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    claim_id,
                    run_id,
                    data.get("support_status"),
                    json.dumps(
                        evidence_ids,
                    ),
                    json.dumps(
                        data,
                        ensure_ascii=False,
                    ),
                ),
            )

    def save_synthesis(
        self,
        run_id: str,
        synthesis: Any,
    ) -> None:
        data = _jsonable(synthesis)

        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO research_syntheses
                (
                    run_id,
                    created_at,
                    payload
                )
                VALUES (?, ?, ?)
                """,
                (
                    run_id,
                    _utc_now(),
                    json.dumps(
                        data,
                        ensure_ascii=False,
                    ),
                ),
            )

    def get_run(
        self,
        run_id: str,
    ) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM research_runs
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()

        if row is None:
            return None

        return {
            "run_id": row["run_id"],
            "question": row["question"],
            "created_at": row["created_at"],
            "payload": json.loads(
                row["payload"]
            ),
        }

    def list_runs(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        if limit < 1:
            raise ValueError(
                "limit must be positive."
            )

        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    run_id,
                    question,
                    created_at
                FROM research_runs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {
                "run_id": row["run_id"],
                "question": row["question"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def counts(
        self,
        run_id: str,
    ) -> dict[str, int]:
        with self._connection() as connection:
            result = {}

            for table, key in (
                ("research_sources", "sources"),
                ("research_evidence", "evidence"),
                ("research_claims", "claims"),
                ("research_syntheses", "syntheses"),
            ):
                row = connection.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {table}
                    WHERE run_id = ?
                    """,
                    (run_id,),
                ).fetchone()

                result[key] = int(row[0])

        return result
