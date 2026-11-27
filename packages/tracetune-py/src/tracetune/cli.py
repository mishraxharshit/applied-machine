"""Command-line entry point:  tracetune build --traces X.jsonl --out Y.jsonl"""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .export import write_dataset
from .filters import select_traces
from .loader import load_traces


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tracetune",
        description="Turn agent production traces into a filtered training dataset.",
    )
    parser.add_argument("--version", action="version", version=f"tracetune {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="score, filter and export traces")
    build.add_argument("--traces", required=True, help="input traces (.jsonl)")
    build.add_argument("--out", required=True, help="output dataset (.jsonl)")
    build.add_argument("--min-score", type=float, default=0.0, help="keep traces scoring >= this (default 0.0)")
    build.add_argument(
        "--dedup",
        choices=["best", "none"],
        default="best",
        help="best: keep only the highest-scoring trace per identical input (default); none: keep all",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        result = select_traces(load_traces(args.traces), min_score=args.min_score, dedup=args.dedup)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    written = write_dataset(result.kept, args.out)

    print(f"traces read : {result.total}")
    print(f"kept        : {written}  -> {args.out}")
    print(f"dropped     : {result.dropped}")
    for reason, count in sorted(result.dropped_by_reason.items()):
        print(f"  - {reason}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
