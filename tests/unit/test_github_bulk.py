from collector.github_bulk import collect_relevant_files


def test_collect_relevant_files(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "collector.github_bulk.RAW_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        "collector.github_bulk.discover_relevant_files",
        lambda: ["README.md", "rag/docs/en.md"],
    )

    monkeypatch.setattr(
        "collector.github_bulk.fetch_github_file",
        lambda path: f"content for {path}",
    )

    result = collect_relevant_files()

    assert len(result) == 2
    assert (tmp_path / "README.md").exists()
    assert (tmp_path / "rag__docs__en.md").exists()
