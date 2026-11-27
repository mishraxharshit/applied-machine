# Trace format

One JSON object per line (JSONL).

| Field | Type | Required | Meaning |
|---|---|---|---|
| `trace_id` | string | yes | unique id of this run |
| `input` | string | yes | what the user asked |
| `output` | string | yes | the agent's final answer (empty if the run crashed) |
| `steps` | list | no | tool calls made, in order |
| `feedback` | 1, -1 or null | no | thumbs up / thumbs down / unknown |
| `error` | string | no | set when the whole run failed |

Each step:

| Field | Type | Meaning |
|---|---|---|
| `name` | string | tool name (required) |
| `args` | object | arguments passed to the tool |
| `result` | string | tool output on success |
| `error` | string | tool error on failure |

## Example
```json
{"trace_id": "t1", "input": "How many customers are in Delhi?",
 "steps": [{"name": "run_sql", "args": {"query": "SELECT COUNT(*) FROM customers WHERE city='Delhi'"}, "result": "3"}],
 "output": "Answer: 3", "feedback": 1}
```

Validation lives in `packages/tracetune-py/src/tracetune/schema.py`. Errors report the file and line number.
