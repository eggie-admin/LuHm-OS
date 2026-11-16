#!/usr/bin/env node
/** Read-only help and local source audit. No command execution or shell interpolation. */
import { help, sourceAudit, registry } from "../src/index.mjs";

const [command, argument, ...extra] = process.argv.slice(2);
const allowed = new Set(["help", "audit", "list"]);
if (!allowed.has(command) || extra.length > 0
    || (command !== "help" && argument !== undefined)
    || (command === "help" && argument !== undefined
        && (argument.length > 160 || !/^[a-zA-Z0-9]+$/.test(argument)))) {
  console.error("usage: luhm-registry help [registeredAlias] | list | audit");
  process.exitCode = 2;
} else if (command === "audit") {
  process.stdout.write(JSON.stringify(sourceAudit(), null, 2) + "\n");
} else if (command === "list" || argument === undefined) {
  const rows = registry.list().map(row => ({
    canonicalName: row.canonical,
    vowelRipped: row.vowelRipped,
    shorthand: row.shorthand,
  }));
  process.stdout.write(JSON.stringify(rows, null, 2) + "\n");
} else {
  const info = help(argument);
  process.stdout.write(JSON.stringify(info, null, 2) + "\n");
  if (info.state === "VERIFY") process.exitCode = 3;
}
