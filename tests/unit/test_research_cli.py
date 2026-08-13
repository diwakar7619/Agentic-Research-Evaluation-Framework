from research.cli import build_parser


def test_cli_requires_question():

    parser = build_parser()

    args = parser.parse_args(
        [
            "What is Qdrant?",
        ]
    )

    assert (
        args.question
        == "What is Qdrant?"
    )

    assert args.sources == 5
    assert args.model == "qwen3:4b"


def test_cli_accepts_runtime_options():

    parser = build_parser()

    args = parser.parse_args(
        [
            "Latest Qdrant architecture",
            "--sources",
            "3",
            "--model",
            "qwen3:4b",
            "--run-id",
            "test-run",
            "--json",
        ]
    )

    assert args.sources == 3
    assert args.model == "qwen3:4b"
    assert args.run_id == "test-run"
    assert args.json is True


def test_cli_help_contract():

    parser = build_parser()

    assert (
        "Research question"
        in parser.format_help()
    )
