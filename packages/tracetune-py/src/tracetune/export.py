"""Turn kept traces into a training dataset.

Output format: one JSON object per line with a "messages" list in the common
chat style (user / assistant / tool). Most fine-tuning tools (TRL, Unsloth,
Axolotl) can read this shape or something very close to it; small adapters
for specific trainers can be added later without changing the core.
"""
from __future__ import annotations

import json
from pathlib import Path

from .schema import Trace


def trace_to_messages(trace: Trace) -> list[dict]:
    messages: list[dict] = [{"role": "user", "content": trace.input}]
    for i, step in enumerate(trace.steps):
        call_id = f"call_{i}"
        messages.append(
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {"name": step.name, "arguments": json.dumps(step.args)},
                    }
                ],
            }
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call_id,
                "content": step.result if step.result is not None else (step.error or ""),
            }
        )
    messages.append({"role": "assistant", "content": trace.output})
    return messages


def write_dataset(kept: list[tuple[Trace, float]], out_path: str | Path) -> int:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for trace, score in kept:
            row = {
                "messages": trace_to_messages(trace),
                "metadata": {"trace_id": trace.trace_id, "score": score},
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(kept)
