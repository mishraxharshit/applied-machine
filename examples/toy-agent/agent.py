"""Toy text-to-SQL "agent" that produces realistic, messy traces.

Why this exists: tracetune needs real-looking data to be tested on. Real agents
make mistakes, retry, wander and sometimes crash. This script imitates that with
a seeded random generator, so results are reproducible (same --seed = same data).

It is rule-based on purpose: no model, no API key, runs on any laptop.

Usage:
    python3 examples/toy-agent/agent.py --n 60 --out data/toy_traces.jsonl
    python3 examples/toy-agent/agent.py --n 60 --ingest http://localhost:8080/v1/traces
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

CITIES = ["Delhi", "Mumbai", "Indore", "Pune"]
YEARS = [2024, 2025]

# (question, good_sql, buggy_sql -> raises an error, wrong_sql -> runs but gives a wrong answer)
TEMPLATES = [
    ("How many customers are in {city}?",
     "SELECT COUNT(*) FROM customers WHERE city='{city}'",
     "SELECT COUNT(*) FROM customers WHERE town='{city}'",
     "SELECT COUNT(*) FROM customers"),
    ("What was the total revenue in {year}?",
     "SELECT SUM(amount) FROM orders WHERE year={year}",
     "SELECT SUM(amount) FROM orders WHERE yr={year}",
     "SELECT SUM(amount) FROM orders"),
    ("How many orders were cancelled?",
     "SELECT COUNT(*) FROM orders WHERE status='cancelled'",
     "SELECT COUNT(*) FROM orders WHERE state='cancelled'",
     "SELECT COUNT(*) FROM orders"),
    ("What is the average order value?",
     "SELECT ROUND(AVG(amount),2) FROM orders",
     "SELECT AVG(amt) FROM orders",
     "SELECT MAX(amount) FROM orders"),
    ("Which customer spent the most?",
     "SELECT c.name FROM customers c JOIN orders o ON o.customer_id=c.id GROUP BY c.id ORDER BY SUM(o.amount) DESC LIMIT 1",
     "SELECT c.name FROM customers c JOIN orders o ON o.cust_id=c.id GROUP BY c.id ORDER BY SUM(o.amount) DESC LIMIT 1",
     "SELECT name FROM customers LIMIT 1"),
]


def make_db(rng: random.Random) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT, city TEXT);
        CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL, year INTEGER, status TEXT);
        """
    )
    names = ["Asha", "Ravi", "Meera", "Kiran", "Neha", "Arjun", "Sana", "Vikram", "Isha", "Rohan"]
    for i, name in enumerate(names, 1):
        conn.execute("INSERT INTO customers VALUES (?,?,?)", (i, name, rng.choice(CITIES)))
    for i in range(1, 41):
        conn.execute(
            "INSERT INTO orders VALUES (?,?,?,?,?)",
            (i, rng.randint(1, 10), rng.randint(100, 2000), rng.choice(YEARS),
             rng.choice(["done", "done", "done", "cancelled"])),
        )
    return conn


def run_sql(conn: sqlite3.Connection, query: str):
    """The agent's only tool. Returns (result, error); exactly one is None."""
    try:
        rows = conn.execute(query).fetchall()
    except sqlite3.Error as e:
        return None, str(e)
    if len(rows) == 1 and len(rows[0]) == 1:
        return str(rows[0][0]), None
    return str(rows), None


def step(query: str, result, error) -> dict:
    s = {"name": "run_sql", "args": {"query": query}}
    if error:
        s["error"] = error
    else:
        s["result"] = result
    return s


def run_agent(rng: random.Random, conn: sqlite3.Connection, i: int) -> dict:
    tpl = rng.choice(TEMPLATES)
    params = {"city": rng.choice(CITIES), "year": rng.choice(YEARS)}
    question, good, buggy, wrong = (t.format(**params) for t in tpl)
    truth, _ = run_sql(conn, good)  # ground truth, used only to simulate user feedback

    trace = {"trace_id": f"toy-{i:04d}", "input": question, "steps": [], "output": ""}

    if rng.random() < 0.05:                      # 5%: the whole run crashes
        trace["error"] = "tool timeout"
        return trace

    steps = trace["steps"]
    if rng.random() < 0.20:                      # 20%: wanders around the database first
        for _ in range(rng.randint(2, 4)):
            q = f"SELECT * FROM {rng.choice(['customers', 'orders'])} LIMIT 3"
            steps.append(step(q, *run_sql(conn, q)))
    if rng.random() < 0.25:                      # 25%: first attempt uses a wrong column name
        steps.append(step(buggy, *run_sql(conn, buggy)))

    final_sql = wrong if rng.random() < 0.20 else good   # 20%: answers wrongly
    result, error = run_sql(conn, final_sql)
    steps.append(step(final_sql, result, error))
    trace["output"] = f"Answer: {result}"

    if rng.random() < 0.60:                      # only 60% of users leave feedback
        trace["feedback"] = 1 if result == truth else -1
    return trace


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate toy agent traces.")
    ap.add_argument("--n", type=int, default=50, help="number of traces")
    ap.add_argument("--seed", type=int, default=42, help="same seed = same traces")
    ap.add_argument("--out", default="data/toy_traces.jsonl", help="write traces to this JSONL file")
    ap.add_argument("--ingest", help="also POST each trace to this URL (the Go ingest service)")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    conn = make_db(rng)
    traces = [run_agent(rng, conn, i) for i in range(args.n)]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(t) + "\n" for t in traces), encoding="utf-8")

    if args.ingest:
        for t in traces:
            req = urllib.request.Request(
                args.ingest, data=json.dumps(t).encode(),
                headers={"Content-Type": "application/json"}, method="POST",
            )
            try:
                urllib.request.urlopen(req, timeout=5).close()
            except (urllib.error.URLError, OSError) as e:
                print(f"error: could not reach {args.ingest}: {e}", file=sys.stderr)
                return 1

    up = sum(t.get("feedback") == 1 for t in traces)
    down = sum(t.get("feedback") == -1 for t in traces)
    crashed = sum("error" in t for t in traces)
    print(f"wrote {len(traces)} traces to {out}")
    print(f"thumbs up: {up}, thumbs down: {down}, no feedback: {len(traces) - up - down}, crashed: {crashed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
