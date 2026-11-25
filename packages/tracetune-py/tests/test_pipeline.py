import json
import tempfile
import unittest
from pathlib import Path

from tracetune.cli import main
from tracetune.export import trace_to_messages
from tracetune.filters import score_trace, select_traces
from tracetune.loader import load_traces
from tracetune.schema import Step, Trace

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_traces.jsonl"


class ScoringTests(unittest.TestCase):
    def test_positive_clean_trace_scores_one(self):
        t = Trace("x", "q", "a", steps=[Step("run_sql", result="ok")], feedback=1)
        self.assertEqual(score_trace(t), 1.0)

    def test_long_wandering_trace_is_penalised(self):
        t = Trace("x", "q", "a", steps=[Step("run_sql", result="ok") for _ in range(7)])
        self.assertAlmostEqual(score_trace(t), -0.4)

    def test_failed_run_scores_negative(self):
        t = Trace("x", "q", "", error="timeout")
        self.assertLess(score_trace(t), 0)


class PipelineTests(unittest.TestCase):
    def test_sample_file_keeps_four_drops_four(self):
        result = select_traces(load_traces(SAMPLE))
        self.assertEqual(result.total, 8)
        self.assertEqual([t.trace_id for t, _ in result.kept], ["t1", "t2", "t3", "t7"])
        self.assertEqual(
            result.dropped_by_reason,
            {"negative_feedback": 1, "trace_error": 1, "low_score": 1, "step_error": 1},
        )

    def test_messages_shape(self):
        t = Trace("x", "q", "final", steps=[Step("run_sql", {"query": "S"}, result="42")])
        roles = [m["role"] for m in trace_to_messages(t)]
        self.assertEqual(roles, ["user", "assistant", "tool", "assistant"])

    def test_bad_json_reports_line_number(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.jsonl"
            p.write_text('{"trace_id": "a", "input": "q", "output": "o"}\nnot json\n')
            with self.assertRaises(ValueError) as ctx:
                list(load_traces(p))
            self.assertIn(":2:", str(ctx.exception))

    def test_cli_writes_dataset(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "out" / "dataset.jsonl"
            code = main(["build", "--traces", str(SAMPLE), "--out", str(out)])
            self.assertEqual(code, 0)
            rows = [json.loads(line) for line in out.read_text().splitlines()]
            self.assertEqual(len(rows), 4)


if __name__ == "__main__":
    unittest.main()
