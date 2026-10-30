#!/usr/bin/env node
/** npm-to-Python source-only command bridge. No shell, user script or network execution. */
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { GoddessOrchestra } from "./orchestra.mjs";

const ops = new GoddessOrchestra();
const here = path.dirname(fileURLToPath(import.meta.url));
const pythonAudit = path.resolve(here, "../../../tools/unifiedGoddessOrchestraAudit.py");
const [command, ...args] = process.argv.slice(2);

if (command === "song" && args.length === 0) {
  console.log(JSON.stringify({ beats: ops.song(), activeWorkers: 0, crown: "STOP" }, null, 2));
} else if (command === "plan" && args.length === 3) {
  try {
    console.log(JSON.stringify(ops.plan(args[0], args[1], args[2]), null, 2));
  } catch (_error) {
    console.error("REJECTED_UNKNOWN_ROUTE");
    process.exitCode = 2;
  }
} else if (["audit", "matrix", "sql-smoke"].includes(command) && args.length === 0) {
  // Windows Python launcher is a convenience, not an implicit installation.
  const python = process.platform === "win32" ? "py" : "python3";
  const pythonArgs = process.platform === "win32"
    ? ["-3", pythonAudit, "--mode", command]
    : [pythonAudit, "--mode", command];
  const result = spawnSync(python, pythonArgs, {
    shell: false, encoding: "utf8", timeout: 15000, maxBuffer: 1_000_000,
    windowsHide: true, stdio: ["ignore", "pipe", "pipe"]
  });
  if (result.error || result.status !== 0) {
    console.error("PYTHON_AUDIT_FAILED");
    process.exitCode = 1;
  } else {
    process.stdout.write(result.stdout);
  }
} else {
  console.error("USAGE: npm run audit | matrix | sql-smoke | song | plan:local");
  process.exitCode = 2;
}
