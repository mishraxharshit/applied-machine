// Single source of truth for the docs version: the Python package version.
// Runs automatically before `npm run dev` and `npm run build`.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const pyproject = readFileSync(resolve(here, "../../../packages/tracetune-py/pyproject.toml"), "utf8");
const match = pyproject.match(/^version\s*=\s*"([^"]+)"/m);
if (!match) {
  console.error("sync-version: could not find version in pyproject.toml");
  process.exit(1);
}
const out = resolve(here, "../src/data/site.json");
mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, JSON.stringify({ version: match[1] }, null, 2) + "\n");
console.log(`docs version -> ${match[1]}`);
