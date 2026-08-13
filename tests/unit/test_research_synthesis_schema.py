from research.synthesizer import ResearchSynthesizer


def test_runtime_schema_restricts_evidence_ids():
    schema = (
        ResearchSynthesizer._build_synthesis_schema(
            (
                "web-1",
                "web-2",
                "web-3",
            )
        )
    )

    evidence_schema = (
        schema["properties"]
        ["claims"]
        ["items"]
        ["properties"]
        ["evidence_ids"]
        ["items"]
    )

    assert evidence_schema == {
        "type": "string",
        "enum": [
            "web-1",
            "web-2",
            "web-3",
        ],
    }


def test_runtime_schema_instances_are_isolated():
    first = (
        ResearchSynthesizer._build_synthesis_schema(
            ("web-1", "web-2")
        )
    )

    second = (
        ResearchSynthesizer._build_synthesis_schema(
            ("source-a", "source-b")
        )
    )

    first_ids = (
        first["properties"]
        ["claims"]
        ["items"]
        ["properties"]
        ["evidence_ids"]
        ["items"]
        ["enum"]
    )

    second_ids = (
        second["properties"]
        ["claims"]
        ["items"]
        ["properties"]
        ["evidence_ids"]
        ["items"]
        ["enum"]
    )

    assert first_ids == [
        "web-1",
        "web-2",
    ]

    assert second_ids == [
        "source-a",
        "source-b",
    ]
