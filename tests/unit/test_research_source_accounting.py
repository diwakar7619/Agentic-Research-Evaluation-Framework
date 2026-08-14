from research.source_accounting import SourceAccounting


def test_source_accounting():
    accounting = SourceAccounting(requested=5)

    accounting.record_discovered(7)
    accounting.record_duplicate(2)

    accounting.record_fetch_attempt(5)
    accounting.record_fetch_success("web-1")
    accounting.record_fetch_success("web-2")
    accounting.record_fetch_failure()

    accounting.record_evidence("web-1")
    accounting.record_evidence("web-2")

    result = accounting.summary()

    assert result["requested"] == 5
    assert result["discovered"] == 7
    assert result["duplicate"] == 2
    assert result["fetch_attempted"] == 5
    assert result["fetch_succeeded"] == 2
    assert result["fetch_failed"] == 1
    assert result["evidence_bearing"] == 2
    assert result["unique_evidence_sources"] == 2
