#!/usr/bin/env node
/** Pure command-line template generator. Outputs only JSON; no writes, downloads or eval. */
import {createModule, validateModule, step, rollDice} from "../src/engine.mjs";
const [mode, a, b, ...extra]=process.argv.slice(2);
try {
  if(extra.length) throw new TypeError("RED_CLI_ARGS");
  if(mode==="scaffold" && b===undefined) {
    const output=createModule(a??"moonlit-archive");
    process.stdout.write(JSON.stringify(output,null,2)+"\n");
  } else if(mode==="demo" && a===undefined && b===undefined) {
    const m=createModule();
    process.stdout.write(JSON.stringify({summary:validateModule(m),
      step:step(m,"gate",0,2026)},null,2)+"\n");
  } else if(mode==="dice" && typeof a==="string" && b===undefined) {
    process.stdout.write(JSON.stringify(rollDice(a,2026))+"\n");
  } else {
    throw new TypeError("RED_CLI_USAGE");
  }
} catch(e) {
  process.stderr.write("LuHm adventure: "+e.message+"\n");
  process.exitCode=2;
}
