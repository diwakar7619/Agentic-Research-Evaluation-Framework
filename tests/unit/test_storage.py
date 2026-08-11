from storage import save_raw_content


def test_save_raw_content(tmp_path, monkeypatch):
    monkeypatch.setattr("storage.RAW_DIR", tmp_path)

    url = "https://example.com/profile"
    content = "AI engineer builds production systems."

    path = save_raw_content(url, content)

    assert path.exists()
    assert path.read_text(encoding="utf-8") == content
    assert path.suffix == ".txt"
