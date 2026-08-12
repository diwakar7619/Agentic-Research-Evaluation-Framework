from __future__ import annotations

import argparse
from http.server import (
    SimpleHTTPRequestHandler,
    ThreadingHTTPServer,
)
from pathlib import Path


def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--root",
        required=True,
    )

    parser.add_argument(
        "--port",
        type=int,
        required=True,
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()

    class Handler(
        SimpleHTTPRequestHandler
    ):

        def __init__(
            self,
            *handler_args,
            **handler_kwargs,
        ):
            super().__init__(
                *handler_args,
                directory=str(root),
                **handler_kwargs,
            )

        def log_message(
            self,
            format,
            *args,
        ):
            pass

    server = ThreadingHTTPServer(
        ("127.0.0.1", args.port),
        Handler,
    )

    print(
        f"fixture-server-ready:{args.port}",
        flush=True,
    )

    server.serve_forever()


if __name__ == "__main__":
    main()
