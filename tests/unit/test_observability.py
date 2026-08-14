from pathlib import Path

from research.observability import (
    TelemetryRun,
    current_run,
)


def test_current_run_context():

    telemetry = TelemetryRun(
        "context-test"
    )

    assert current_run() is None

    with telemetry:

        assert (
            current_run()
            is telemetry
        )

    assert current_run() is None


def test_nested_spans():

    telemetry = TelemetryRun(
        "span-test"
    )

    with telemetry:

        with telemetry.span(
            "research.run"
        ):

            with telemetry.span(
                "research.plan"
            ):
                pass

    payload = telemetry.snapshot()

    assert len(
        payload["spans"]
    ) == 2

    assert (
        payload["spans"][1]
        ["parent_span_id"]
        ==
        payload["spans"][0]
        ["span_id"]
    )


def test_histogram_percentiles():

    telemetry = TelemetryRun(
        "histogram-test"
    )

    for value in (
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
    ):

        telemetry.observe(
            "test.duration",
            value,
        )

    histogram = (
        telemetry.snapshot()
        ["metrics"]
        ["histograms"]
        ["test.duration"]
    )

    assert histogram["count"] == 5
    assert histogram["p50"] == 0.3


def test_counters_and_events():

    telemetry = TelemetryRun(
        "metric-test"
    )

    telemetry.increment(
        "requests"
    )

    telemetry.increment(
        "requests",
        2,
    )

    telemetry.event(
        "test.completed",
        status="success",
    )

    payload = telemetry.snapshot()

    assert (
        payload["metrics"]
        ["counters"]
        ["requests"]
        == 3
    )

    assert (
        payload["events"][0]["name"]
        == "test.completed"
    )


def test_json_artifact(tmp_path):

    telemetry = TelemetryRun(
        "artifact-test"
    )

    output = telemetry.write(
        directory=tmp_path
    )

    assert Path(output).exists()

    assert (
        Path(output).read_text(
            encoding="utf-8"
        ).strip()
    )
