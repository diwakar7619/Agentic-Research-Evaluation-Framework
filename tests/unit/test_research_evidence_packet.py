from research.evidence_packet import (
    build_evidence_packet,
    render_evidence_packet,
)


def evidence(source_id: str, text: str):
    return {
        "source_id": source_id,
        "source_url": f"https://example.com/{source_id}",
        "text": text,
    }


def test_global_budget_is_enforced():
    items = [
        evidence(
            f"web-{index}",
            (
                "production AI agent research "
                "retrieval scalability evidence "
                * 1000
            ),
        )
        for index in range(10)
    ]

    packet = build_evidence_packet(
        "production AI agent research retrieval scalability evidence",
        items,
        max_total_chars=5000,
        max_per_source_chars=1500,
    )

    rendered = render_evidence_packet(packet)

    assert len(rendered) <= 5000
    assert packet


def test_per_source_budget_is_enforced():
    items = [
        evidence(
            "web-1",
            "production AI research " * 1000,
        ),
    ]

    packet = build_evidence_packet(
        "production AI research",
        items,
        max_total_chars=20_000,
        max_per_source_chars=1000,
    )

    assert len(packet) == 1
    assert len(packet[0].text) <= 1000


def test_duplicate_sources_are_removed():
    items = [
        evidence(
            "web-1",
            "production AI research",
        ),
        evidence(
            "web-1",
            "duplicate production AI research",
        ),
    ]

    packet = build_evidence_packet(
        "production AI research",
        items,
    )

    assert len(packet) == 1
    assert packet[0].source_id == "web-1"


def test_source_diversity_is_preserved():
    items = [
        evidence(
            "web-1",
            "production AI research " * 500,
        ),
        evidence(
            "web-2",
            "production AI retrieval " * 500,
        ),
        evidence(
            "web-3",
            "production AI scalability " * 500,
        ),
        evidence(
            "web-4",
            "production AI evidence " * 500,
        ),
    ]

    packet = build_evidence_packet(
        "production AI research retrieval scalability evidence",
        items,
        max_total_chars=4000,
        max_per_source_chars=1000,
    )

    assert len(packet) == 4

    assert {
        item.source_id
        for item in packet
    } == {
        "web-1",
        "web-2",
        "web-3",
        "web-4",
    }


def test_relevant_source_beats_irrelevant_source():
    items = [
        evidence(
            "irrelevant",
            "cooking recipes vegetables dinner " * 100,
        ),
        evidence(
            "relevant",
            "production AI agent research " * 100,
        ),
    ]

    packet = build_evidence_packet(
        "production AI agent research",
        items,
        max_total_chars=1000,
        max_per_source_chars=800,
    )

    assert packet[0].source_id == "relevant"


def test_empty_evidence_returns_empty_packet():
    packet = build_evidence_packet(
        "production AI research",
        [],
    )

    assert packet == ()


def test_invalid_budget_is_rejected():
    try:
        build_evidence_packet(
            "test",
            [],
            max_total_chars=0,
        )
    except ValueError:
        return

    raise AssertionError(
        "Invalid evidence budget must fail."
    )


def test_rendered_packet_contains_source_identity():
    packet = build_evidence_packet(
        "production AI research",
        [
            evidence(
                "web-1",
                "production AI research evidence",
            )
        ],
    )

    rendered = render_evidence_packet(packet)

    assert "EVIDENCE_ID: web-1" in rendered
    assert "SOURCE: https://example.com/web-1" in rendered
    assert "production AI research evidence" in rendered
