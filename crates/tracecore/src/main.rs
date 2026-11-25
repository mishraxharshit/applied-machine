// tracecore: fast, memory-light preprocessing for huge trace files.
// Why Rust: when trace files reach many GB, streaming + zero-GC speed matters.
// Today: drop invalid lines and duplicate inputs. Later: hashing, near-dup detection.
use serde_json::Value;
use std::collections::HashSet;
use std::fs::File;
use std::io::{BufRead, BufReader, BufWriter, Write};

fn main() -> std::io::Result<()> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        eprintln!("usage: tracecore <in.jsonl> <out.jsonl>");
        std::process::exit(2);
    }
    let reader = BufReader::new(File::open(&args[1])?);
    let mut out = BufWriter::new(File::create(&args[2])?);
    let mut seen: HashSet<String> = HashSet::new();
    let (mut total, mut kept) = (0usize, 0usize);

    for (i, line) in reader.lines().enumerate() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        total += 1;
        let v: Value = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(e) => {
                eprintln!("line {}: {e}", i + 1);
                continue;
            }
        };
        let key = v.get("input").and_then(Value::as_str).unwrap_or("").to_owned();
        if seen.insert(key) {
            writeln!(out, "{line}")?;
            kept += 1;
        }
    }
    eprintln!("read {total}, kept {kept}, dropped {}", total - kept);
    Ok(())
}
