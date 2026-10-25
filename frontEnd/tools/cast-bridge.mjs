#!/usr/bin/env node
/**
 * npm-facing, human-in-the-loop CAST preview.
 * No package install, network call, builder, shell, approval, or mutation path.
 */
import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const valueFlags = new Set(["--tier", "--tasks", "--scope-id", "--source-ref", "--phase", "--register", "--intent"]);
const switches = new Map([
  ["-h", "help"], ["--help", "help"],
  ["-d", "docs"], ["--docs", "docs"],
  ["-v", "verbose"], ["--verbose", "verbose"],
  ["-f", "forceRequested"], ["--force", "forceRequested"],
  ["--dry-run", "dryRun"], ["--json", "json"]
]);
const phases = new Set(["conceptDevelopment", "developmentWorkspace", "castBridge", "finalCastEvidence"]);
const registers = new Set(["friend", "underclassman", "assistant", "colleague"]);
const allowedKeys = new Map([
  ["--tier", "tier"], ["--tasks", "tasks"], ["--scope-id", "scopeId"],
  ["--source-ref", "sourceRef"], ["--phase", "phase"], ["--register", "register"], ["--intent", "intent"]
]);

export function parseOptions(argv) {
  const options = {
    tier: 0, tasks: ["mobileMainHost", "chatGptInlineMount"],
    scopeId: "professor/cast-bridge", sourceRef: null,
    phase: "castBridge", register: "assistant", intent: "",
    help: false, docs: false, verbose: false, forceRequested: false,
    dryRun: true, json: false
  };
  const seen = new Set();
  for (let index = 0; index < argv.length; index++) {
    let token = argv[index];
    const equal = token.indexOf("=");
    let rawValue = null;
    if (equal !== -1) {
      rawValue = token.slice(equal + 1);
      token = token.slice(0, equal);
    }
    if (switches.has(token)) {
      if (rawValue !== null) throw new Error(token + " is a boolean switch");
      options[switches.get(token)] = true;
      continue;
    }
    if (!valueFlags.has(token)) throw new Error("Unrecognized CAST option: " + token);
    if (seen.has(token)) throw new Error("Duplicate CAST option: " + token);
    seen.add(token);
    const value = rawValue ?? argv[++index];
    if (typeof value !== "string" || value.length === 0 || value.startsWith("--")) {
      throw new Error("Missing value for " + token);
    }
    const key = allowedKeys.get(token);
    if (key === "tier") {
      if (!/^[0-3]$/.test(value)) throw new Error("Escalation tier must be an integer 0..3");
      options.tier = Number(value);
    } else if (key === "tasks") {
      const tasks = value.split(",").map(x => x.trim());
      if (tasks.length < 1 || tasks.length > 8 ||
          tasks.some(x => !/^[a-z][A-Za-z0-9]*$/.test(x)) ||
          new Set(tasks).size !== tasks.length) throw new Error("Select 1..8 unique canonical task IDs");
      options.tasks = tasks;
    } else if (key === "sourceRef") {
      if (!/^[a-f0-9]{40}$/.test(value)) throw new Error("source-ref must be 40 lowercase hex characters");
      options.sourceRef = value;
    } else if (key === "scopeId") {
      if (!/^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$/.test(value)) throw new Error("Invalid scope-id");
      options.scopeId = value;
    } else if (key === "phase") {
      if (!phases.has(value)) throw new Error("Unknown CAST presentation phase");
      options.phase = value;
    } else if (key === "register") {
      if (!registers.has(value)) throw new Error("Unknown human collaboration register");
      options.register = value;
    } else if (key === "intent") {
      if (value.length > 280 || /[\u0000-\u001f\u007f]/.test(value)) {
        throw new Error("Human intent must be a single bounded text line");
      }
      options.intent = value; // Context for review, never execution instructions.
    }
  }
  return options;
}

export const helpText = [
  "CAST bridge | npm human-in-the-loop preview (NO dispatch)",
  "",
  "npm run cast:preview -- [options]",
  "  -h, --help            Help",
  "  -d, --docs            Explain the evidence and human approval boundary",
  "  -v, --verbose         Include evidence expectations",
  "  -f, --force           Record escalation REQUEST only; cannot override a gate",
  "      --tier 0..3       Audit depth; default 0 (typed integer)",
  "      --tasks a,b       Existing queue task IDs, max 8",
  "      --intent TEXT     Human request label; never evaluated or executed",
  "      --source-ref SHA  Exact lowercase 40-hex Git source (default checkout HEAD)",
  "      --scope-id ID     Narrow scope; default professor/cast-bridge",
  "      --register NAME   friend|underclassman|assistant|colleague",
  "      --phase NAME      conceptDevelopment|developmentWorkspace|castBridge|finalCastEvidence",
  "      --json            Machine-readable receipt",
  "      --dry-run         Explicit safe default; never execute a build",
  "",
  "Example: npm run cast:preview -- -v --tier 0 --intent 'show mobile proof'",
  "The GitHub owner-authored /cast trigger remains the ONLY build dispatch boundary."
].join("\n");

const docsText = [
  helpText, "",
  "Human-in-the-loop contract",
  "  1. Capture typed human intent and existing canonical task IDs.",
  "  2. Pin sourceRef from this git checkout, NOT a claim about live Render.",
  "  3. Ask the existing Python bridge for a read-only queue/evidence preview.",
  "  4. Show the missing receipt(s). A human decides whether to pursue approval.",
  "  5. Build, install, merge, deployment and Crown remain separate authorized gates.",
  "Tier 0 is the default. Tier 3 means greater audit depth, never more authority.",
  "Force is a REQUEST FOR REVIEW, not an override. No npm lifecycle installation.",
  "Preserve exact LuHm-OS brand, lowercase kebab display slugs and internal camelHump IDs."
].join("\n");

function readHead() {
  const run = spawnSync("git", ["rev-parse", "HEAD"], {
    cwd: repoRoot, encoding: "utf8", timeout: 5000, shell: false
  });
  const sha = (run.stdout || "").trim();
  if (run.status !== 0 || !/^[a-f0-9]{40}$/.test(sha)) {
    throw new Error("No exact git HEAD available; pass --source-ref explicitly");
  }
  return sha;
}

export function checkReceipt(packet, options, sourceRef) {
  if (packet?.schema !== "luhmOs.humanCenteredCastPreview.v1" ||
      packet.status !== "READ_ONLY_SOURCE_CANDIDATE_NOT_HOST_MOUNTED" ||
      packet.sourceRef !== sourceRef || packet.scopeId !== options.scopeId ||
      packet.workflowPhase !== options.phase ||
      packet.castEnvelopesGranted !== 0 || packet.buildDispatched !== false ||
      packet.agentWorkersStarted !== 0 || packet.hostMountVerified !== false ||
      packet.releaseAuthorized !== false || packet.crownGranted !== false ||
      packet.crownStatus !== "STOP" ||
      !Array.isArray(packet.tasks) || packet.taskCount !== options.tasks.length ||
      packet.tasks.some(t => t.buildDispatched !== false || t.sourceMutated !== false)) {
    throw new Error("CAST bridge refused an unverified or authority-changing receipt");
  }
  return true;
}

export function preview(options) {
  const sourceRef = options.sourceRef ?? readHead();
  const args = [
    "tools/castHumanCenteredBridge.py", "--tasks", options.tasks.join(","),
    "--source-ref", sourceRef, "--scope-id", options.scopeId,
    "--register", options.register, "--phase", options.phase,
    "--tier", String(options.tier)
  ];
  const run = spawnSync("python3", args, {
    cwd: repoRoot, encoding: "utf8", timeout: 15000,
    maxBuffer: 1024 * 1024, shell: false
  });
  if (run.error || run.status !== 0) {
    throw new Error("Canonical CAST preview failed closed. " + (run.error?.message || (run.stderr || "").slice(0, 300)));
  }
  let packet;
  try { packet = JSON.parse(run.stdout); }
  catch { throw new Error("Canonical CAST preview returned invalid JSON"); }
  checkReceipt(packet, options, sourceRef);
  return {
    schema: "luhmOs.npmCastHumanBoundary.v1",
    status: "READ_ONLY_REVIEW_REQUIRED",
    sourceRef,
    sourceRefMeaning: "EXACT_CHECKOUT_HEAD_NOT_LIVE_RUNTIME_PROOF",
    scopeId: options.scopeId,
    intent: options.intent || "Preview queued CAST readiness",
    escalationTier: options.tier,
    workflowPhase: options.phase,
    humanRegister: options.register,
    forceRequested: options.forceRequested,
    forceApplied: false,
    humanDecisionRequired: true,
    dispatchAuthority: false,
    nextBoundary: packet.tasks.map(t => ({
      taskId: t.taskId,
      priority: t.priority,
      next: t.smallestNextAction,
      evidenceRequired: t.evidenceRequired,
      dependsOn: t.dependsOn
    })),
    canonicalPreview: packet,
    crownStatus: "STOP"
  };
}

export function formatHuman(receipt, verbose = false) {
  const lines = [
    "CAST bridge: READ ONLY | Crown STOP",
    "Source: " + receipt.sourceRef + " (checkout, not live deployment proof)",
    "Scope: " + receipt.scopeId + " | tier " + receipt.escalationTier,
    "Intent: " + receipt.intent,
    "Human decision: REQUIRED | build dispatch: NO",
    receipt.forceRequested ? "FORCE request recorded; gate override DENIED" : "Force: not requested"
  ];
  for (const [index, task] of receipt.nextBoundary.entries()) {
    lines.push(String(index + 1) + ". " + task.taskId + ": " + task.next);
    if (verbose) lines.push("   Evidence: " + task.evidenceRequired.join("; "));
  }
  return lines.join("\n");
}

function main() {
  try {
    const options = parseOptions(process.argv.slice(2));
    if (options.help || options.docs) {
      process.stdout.write((options.docs ? docsText : helpText) + "\n");
      return;
    }
    const receipt = preview(options);
    process.stdout.write((options.json ? JSON.stringify(receipt, null, 2) : formatHuman(receipt, options.verbose)) + "\n");
  } catch (error) {
    process.stderr.write("CAST_PREVIEW_BLOCKED: " + error.message + "\n");
    process.exitCode = 2;
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
