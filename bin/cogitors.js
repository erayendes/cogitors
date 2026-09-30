#!/usr/bin/env node
// Thin launcher: the engine is Python (3.9+, stdlib only); pass every argument through.
const { spawnSync } = require("node:child_process");
const path = require("node:path");

const script = path.join(__dirname, "..", "skills", "cogitors", "scripts", "cogitor.py");
const python = process.env.COGITORS_PYTHON || "python3";
const result = spawnSync(python, [script, ...process.argv.slice(2)], { stdio: "inherit" });

if (result.error) {
  console.error(`cogitors: could not run ${python} (${result.error.code}). Install Python 3.9+ or set COGITORS_PYTHON.`);
  process.exit(1);
}
process.exit(result.status ?? 1);
