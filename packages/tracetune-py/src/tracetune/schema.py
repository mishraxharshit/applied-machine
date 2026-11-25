"""The data model: what a 'trace' means in tracetune.

Everything else in the project (loading, scoring, exporting) depends on this
file, so keep it small and boring. If you change it, you change the contract
with every user's data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Step:
    """One tool call made by the agent."""

    name: str
    args: dict[str, Any] = field(default_factory=dict)
    result: Optional[str] = None
    error: Optional[str] = None


@dataclass
class Trace:
    """One full agent run: a user input, the steps taken, and the final answer."""

    trace_id: str
    input: str
    output: str
    steps: list[Step] = field(default_factory=list)
    feedback: Optional[int] = None  # +1 (thumbs up), -1 (thumbs down), None (unknown)
    error: Optional[str] = None  # set when the whole run failed

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Trace":
        # Fail early with a clear message: bad data is the #1 source of bad models.
        for key in ("trace_id", "input", "output"):
            if key not in d:
                raise ValueError(f"trace is missing required field '{key}'")

        steps = []
        for i, s in enumerate(d.get("steps", [])):
            if "name" not in s:
                raise ValueError(f"step {i} of trace {d['trace_id']!r} has no 'name'")
            steps.append(
                Step(
                    name=s["name"],
                    args=s.get("args", {}),
                    result=s.get("result"),
                    error=s.get("error"),
                )
            )

        feedback = d.get("feedback")
        if feedback not in (None, 1, -1):
            raise ValueError(f"feedback must be 1, -1 or null, got {feedback!r}")

        return cls(
            trace_id=str(d["trace_id"]),
            input=d["input"],
            output=d["output"],
            steps=steps,
            feedback=feedback,
            error=d.get("error"),
        )
