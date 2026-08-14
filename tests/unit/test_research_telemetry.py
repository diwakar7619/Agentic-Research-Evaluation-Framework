from research.telemetry import ResearchTelemetry


def test_telemetry_records_stage():
    telemetry = ResearchTelemetry("test-run")

    with telemetry.stage("collection"):
        pass

    result = telemetry.summary()

    assert result["run_id"] == "test-run"
    assert len(result["stages"]) == 1
    assert result["stages"][0]["name"] == "collection"
    assert result["stages"][0]["success"] is True
    assert result["stages"][0]["elapsed_seconds"] >= 0


def test_telemetry_records_failed_stage():
    telemetry = ResearchTelemetry("test-run")

    try:
        with telemetry.stage("extraction"):
            raise RuntimeError("boom")
    except RuntimeError:
        pass

    result = telemetry.summary()

    assert result["stages"][0]["success"] is False


def test_telemetry_counters():
    telemetry = ResearchTelemetry("test-run")

    telemetry.increment("sources_discovered", 5)
    telemetry.increment("sources_discovered", 2)

    assert telemetry.summary()["counters"][
        "sources_discovered"
    ] == 7
