"""Reward scoring and filtering: the 'brain' of tracetune.

Idea: not every production trace is good training data. We give each trace a
numeric score (a simple reward function) and keep only the good ones.

Every number here is a *design choice*, not a law of nature. That is why they
live in RewardConfig: users can tune them without touching code.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .schema import Trace


@dataclass(frozen=True)
class RewardConfig:
    positive_feedback: float = 1.0
    negative_feedback: float = -1.0
    step_error_penalty: float = 1.0     # per failed tool call
    trace_error_penalty: float = 2.0    # whole run failed
    free_steps: int = 3                 # steps allowed with no penalty
    extra_step_penalty: float = 0.1     # per step beyond free_steps (prefers efficient agents)


DEFAULT_REWARD = RewardConfig()


def score_trace(trace: Trace, cfg: RewardConfig = DEFAULT_REWARD) -> float:
    score = 0.0
    if trace.feedback == 1:
        score += cfg.positive_feedback
    elif trace.feedback == -1:
        score += cfg.negative_feedback

    score -= cfg.step_error_penalty * sum(1 for s in trace.steps if s.error)

    if trace.error:
        score -= cfg.trace_error_penalty

    extra_steps = max(0, len(trace.steps) - cfg.free_steps)
    score -= cfg.extra_step_penalty * extra_steps
    return round(score, 6)


def drop_reason(trace: Trace) -> str:
    """Human-readable reason a trace was dropped. Order = most serious first."""
    if trace.error:
        return "trace_error"
    if trace.feedback == -1:
        return "negative_feedback"
    if any(s.error for s in trace.steps):
        return "step_error"
    return "low_score"


@dataclass
class SelectionResult:
    kept: list[tuple[Trace, float]] = field(default_factory=list)
    dropped_by_reason: dict[str, int] = field(default_factory=dict)
    total: int = 0

    @property
    def dropped(self) -> int:
        return sum(self.dropped_by_reason.values())


def select_traces(
    traces,
    min_score: float = 0.0,
    cfg: RewardConfig = DEFAULT_REWARD,
) -> SelectionResult:
    result = SelectionResult()
    for trace in traces:
        result.total += 1
        score = score_trace(trace, cfg)
        if score >= min_score:
            result.kept.append((trace, score))
        else:
            reason = drop_reason(trace)
            result.dropped_by_reason[reason] = result.dropped_by_reason.get(reason, 0) + 1
    return result
