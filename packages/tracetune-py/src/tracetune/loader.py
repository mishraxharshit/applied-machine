"""Read traces from a JSONL file (one JSON object per line).

JSONL is used instead of one big JSON array because it can be streamed,
appended to, and read line by line without loading everything into memory.
Later, importers for Langfuse / OpenTelemetry exports will live next to this.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from .schema import Trace


def load_traces(path: str | Path) -> Iterator[Trace]:
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as e:
                # Always tell the user WHICH line is broken.
                raise ValueError(f"{path}:{line_no}: invalid JSON ({e.msg})") from e
            try:
                yield Trace.from_dict(raw)
            except ValueError as e:
                raise ValueError(f"{path}:{line_no}: {e}") from e
