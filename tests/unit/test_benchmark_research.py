from scripts.benchmark_research import classify_runs


def make_run(
    *,
    exit_code: int = 0,
    failed_steps: int = 0,
    warmup: bool = False,
    requested_sources: int = 5,
) -> dict:
    return {
        "run_id": "test-run",
        "requested_sources": requested_sources,
        "repetition": 1,
        "warmup": warmup,
        "exit_code": exit_code,
        "wall_time_seconds": 1.0,
        "failed_steps": failed_steps,
    }


def test_run_with_failed_step_is_not_successful():
    runs = [
        make_run(exit_code=0, failed_steps=1),
    ]

    successful, failed = classify_runs(runs)

    assert successful == []
    assert len(failed) == 1


def test_zero_exit_and_zero_failed_steps_is_successful():
    runs = [
        make_run(exit_code=0, failed_steps=0),
    ]

    successful, failed = classify_runs(runs)

    assert len(successful) == 1
    assert failed == []


def test_nonzero_exit_code_is_failed():
    runs = [
        make_run(exit_code=1, failed_steps=0),
    ]

    successful, failed = classify_runs(runs)

    assert successful == []
    assert len(failed) == 1


def test_warmup_is_excluded_from_benchmark_results():
    runs = [
        make_run(
            exit_code=0,
            failed_steps=0,
            warmup=True,
        ),
    ]

    successful, failed = classify_runs(runs)

    assert successful == []
    assert failed == []
