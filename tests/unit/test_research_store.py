from __future__ import annotations

from dataclasses import dataclass

import pytest

from research.store import ResearchStore


@dataclass
class FakeEvidence:
    source_id: str
    source_url: str
    text: str


@dataclass
class FakeClaim:
    claim_id: str
    text: str
    evidence_ids: tuple[str, ...]
    support_status: str


def test_store_creates_schema(tmp_path):
    path = tmp_path / "research.db"

    ResearchStore(path)

    assert path.exists()


def test_save_and_get_run(tmp_path):
    store = ResearchStore(
        tmp_path / "research.db"
    )

    store.save_run(
        "run-1",
        "Test research question",
        {
            "status": "completed",
            "steps": 2,
        },
    )

    result = store.get_run("run-1")

    assert result is not None
    assert result["run_id"] == "run-1"
    assert result["question"] == (
        "Test research question"
    )
    assert result["payload"]["status"] == (
        "completed"
    )


def test_save_source_evidence_and_claim(tmp_path):
    store = ResearchStore(
        tmp_path / "research.db"
    )

    store.save_run(
        "run-1",
        "Question",
        {},
    )

    store.save_source(
        "run-1",
        {
            "source_id": "source-1",
            "source_url": "https://example.com",
            "canonical_url": "https://example.com",
            "content_hash": "abc",
        },
    )

    evidence = FakeEvidence(
        source_id="source-1",
        source_url="https://example.com",
        text="Evidence text.",
    )

    store.save_evidence(
        "run-1",
        evidence,
    )

    claim = FakeClaim(
        claim_id="claim-1",
        text="Supported claim.",
        evidence_ids=("source-1",),
        support_status="single_source",
    )

    store.save_claim(
        "run-1",
        claim,
    )

    counts = store.counts("run-1")

    assert counts == {
        "sources": 1,
        "evidence": 1,
        "claims": 1,
        "syntheses": 0,
    }


def test_save_synthesis(tmp_path):
    store = ResearchStore(
        tmp_path / "research.db"
    )

    store.save_run(
        "run-1",
        "Question",
        {},
    )

    store.save_synthesis(
        "run-1",
        {
            "answer": "Answer",
            "sources_used": 1,
        },
    )

    assert store.counts(
        "run-1"
    )["syntheses"] == 1


def test_missing_run_id_rejected(tmp_path):
    store = ResearchStore(
        tmp_path / "research.db"
    )

    with pytest.raises(ValueError):
        store.save_run(
            "",
            "Question",
            {},
        )


def test_missing_source_id_rejected(tmp_path):
    store = ResearchStore(
        tmp_path / "research.db"
    )

    with pytest.raises(ValueError):
        store.save_source(
            "run-1",
            {
                "source_url": "https://example.com"
            },
        )


def test_list_runs(tmp_path):
    store = ResearchStore(
        tmp_path / "research.db"
    )

    store.save_run(
        "run-1",
        "First",
        {},
    )

    store.save_run(
        "run-2",
        "Second",
        {},
    )

    runs = store.list_runs()

    assert len(runs) == 2
    assert {
        item["run_id"]
        for item in runs
    } == {"run-1", "run-2"}


def test_identifiers_are_scoped_to_run(tmp_path):
    store = ResearchStore(
        tmp_path / "research.db"
    )

    for run_id in ("run-1", "run-2"):
        store.save_run(
            run_id,
            f"Question {run_id}",
            {},
        )

        store.save_source(
            run_id,
            {
                "source_id": "source-1",
                "source_url": "https://example.com",
            },
        )

        store.save_evidence(
            run_id,
            {
                "source_id": "source-1",
                "source_url": "https://example.com",
                "text": f"Evidence {run_id}",
            },
        )

        store.save_claim(
            run_id,
            {
                "claim_id": "claim-1",
                "text": f"Claim {run_id}",
                "evidence_ids": ["source-1"],
                "support_status": "single_source",
            },
        )

    assert store.counts("run-1") == {
        "sources": 1,
        "evidence": 1,
        "claims": 1,
        "syntheses": 0,
    }

    assert store.counts("run-2") == {
        "sources": 1,
        "evidence": 1,
        "claims": 1,
        "syntheses": 0,
    }


def test_persistence_survives_reopen(tmp_path):
    path = tmp_path / "research.db"

    first = ResearchStore(path)

    first.save_run(
        "persistent-run",
        "Persistent question",
        {"status": "completed"},
    )

    del first

    second = ResearchStore(path)

    result = second.get_run(
        "persistent-run"
    )

    assert result is not None
    assert result["question"] == (
        "Persistent question"
    )
