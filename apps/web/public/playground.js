// Browser port of tracetune scoring + dedup + export (see packages/tracetune-py/src/tracetune/filters.py).
// Keep CFG in sync with RewardConfig. Runs fully in the browser: nothing is uploaded.
const CFG = { pos: 1, neg: -1, stepErr: 1, traceErr: 2, freeSteps: 3, extra: 0.1 };

function parseJsonl(text) {
  const out = [];
  text.split("\n").forEach((line, i) => {
    line = line.trim();
    if (!line) return;
    let o;
    try { o = JSON.parse(line); } catch (e) { throw new Error("line " + (i + 1) + ": invalid JSON"); }
    for (const k of ["trace_id", "input", "output"]) {
      if (!(k in o)) throw new Error("line " + (i + 1) + ": missing '" + k + "'");
    }
    if (![undefined, null, 1, -1].includes(o.feedback)) throw new Error("line " + (i + 1) + ": feedback must be 1, -1 or null");
    out.push({ id: String(o.trace_id), input: o.input, output: o.output, steps: o.steps || [], feedback: o.feedback ?? null, error: o.error || null });
  });
  return out;
}

function score(t) {
  let s = 0;
  if (t.feedback === 1) s += CFG.pos; else if (t.feedback === -1) s += CFG.neg;
  s -= CFG.stepErr * t.steps.filter((x) => x.error).length;
  if (t.error) s -= CFG.traceErr;
  s -= CFG.extra * Math.max(0, t.steps.length - CFG.freeSteps);
  return Math.round(s * 1e6) / 1e6;
}

function reason(t) {
  if (t.error) return "trace_error";
  if (t.feedback === -1) return "negative_feedback";
  if (t.steps.some((x) => x.error)) return "step_error";
  return "low_score";
}

// Score first, then keep the best run per identical input, then apply min score.
function select(traces, minScore, dedup) {
  const rows = traces.map((t) => ({ t, score: score(t), status: "kept", why: "" }));
  if (dedup) {
    const best = new Map();
    for (const r of rows) {
      const c = best.get(r.t.input);
      if (!c || r.score > c.score) best.set(r.t.input, r);
    }
    for (const r of rows) if (best.get(r.t.input) !== r) { r.status = "dropped"; r.why = "duplicate"; }
  }
  for (const r of rows) if (r.status === "kept" && r.score < minScore) { r.status = "dropped"; r.why = reason(r.t); }
  return rows;
}

function toMessages(t) {
  const m = [{ role: "user", content: t.input }];
  t.steps.forEach((s, i) => {
    const id = "call_" + i;
    m.push({ role: "assistant", content: "", tool_calls: [{ id, type: "function", function: { name: s.name, arguments: JSON.stringify(s.args || {}) } }] });
    m.push({ role: "tool", tool_call_id: id, content: s.result != null ? s.result : (s.error || "") });
  });
  m.push({ role: "assistant", content: t.output });
  return m;
}

function toDataset(rows) {
  return rows.filter((r) => r.status === "kept")
    .map((r) => JSON.stringify({ messages: toMessages(r.t), metadata: { trace_id: r.t.id, score: r.score } })).join("\n");
}

function sampleText() {
  const q = "SELECT x";
  const st = (r, e) => (e ? { name: "run_sql", args: { query: q }, error: e } : { name: "run_sql", args: { query: q }, result: r });
  const rows = [
    { trace_id: "t1", input: "How many customers are in Delhi?", steps: [st("42")], output: "There are 42.", feedback: 1 },
    { trace_id: "t2", input: "List all product categories.", steps: [st("toys, books")], output: "toys, books" },
    { trace_id: "t3", input: "Total revenue in 2025?", steps: [st(null, "no such column: yr"), st("1250000")], output: "1,250,000", feedback: 1 },
    { trace_id: "t4", input: "Which city has the most orders?", steps: [st("Mumbai")], output: "Mumbai", feedback: -1 },
    { trace_id: "t4b", input: "Which city has the most orders?", steps: [st("Pune")], output: "Pune", feedback: 1 },
    { trace_id: "t5", input: "Delete all test users.", steps: [], output: "", error: "tool timeout" },
    { trace_id: "t6", input: "Average order value?", steps: Array(7).fill(0).map(() => st("...")), output: "830" },
    { trace_id: "t8", input: "How many orders were cancelled?", steps: [st(null, "table locked")], output: "I could not find that." },
  ];
  return rows.map((r) => JSON.stringify(r)).join("\n");
}

if (typeof module !== "undefined") module.exports = { parseJsonl, score, select, toDataset, sampleText };

if (typeof document !== "undefined") {
  const $ = (id) => document.getElementById(id);
  $("sample").onclick = () => { $("input").value = sampleText(); };
  $("run").onclick = () => {
    $("error").textContent = "";
    try {
      const rows = select(parseJsonl($("input").value), parseFloat($("min").value) || 0, $("dedup").checked);
      const kept = rows.filter((r) => r.status === "kept").length;
      $("stats").textContent = rows.length + " traces read, " + kept + " kept, " + (rows.length - kept) + " dropped";
      const tb = $("rows");
      tb.textContent = "";
      for (const r of rows) {
        const tr = document.createElement("tr");
        tr.className = r.status;
        [r.t.id, r.t.input, r.score.toFixed(2), r.status === "kept" ? "kept" : "dropped: " + r.why].forEach((v) => {
          const td = document.createElement("td"); td.textContent = v; tr.appendChild(td);
        });
        tb.appendChild(tr);
      }
      $("dataset").value = toDataset(rows);
      $("results").hidden = false;
    } catch (e) { $("error").textContent = "Error: " + e.message; $("results").hidden = true; }
  };
  $("download").onclick = () => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([$("dataset").value + "\n"], { type: "application/jsonl" }));
    a.download = "dataset.jsonl"; a.click();
  };
}
