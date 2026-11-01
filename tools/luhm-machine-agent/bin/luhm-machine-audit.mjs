#!/usr/bin/env node
/** Restricted local-only entrypoint, not a model or remotely executing agent. */
import { spawnSync } from "node:child_process";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { auditSource, loadPolicy, planTask, remotePlan, repoRoot } from "../src/index.mjs";
import {checkRegistry, encodePacket, decodePacket} from "../src/device-registry.mjs";

function fail(message){
  process.stderr.write("RED_LOCAL_AUDIT: "+message.replace(/[^\w .:-]/g,"_").slice(0,160)+"\n");
  process.exitCode=2;
}
async function main(){
  const args=process.argv.slice(2);
  const cmd=args.shift();
  if(!["audit","verify","plan","remote-plan"].includes(cmd)){
    throw new Error("UNKNOWN_COMMAND");
  }
  let withPython=false, withDevice=false, task=null;
  for(let i=0;i<args.length;i++){
    if(cmd==="audit" && args[i]==="--with-python" && !withPython){withPython=true;continue;}
    if(cmd==="audit" && args[i]==="--with-device" && !withDevice){withDevice=true;continue;}
    if(cmd==="plan" && args[i]==="--task" && task===null && i+1<args.length){
      task=args[++i];continue;
    }
    throw new Error("UNKNOWN_ARGUMENT");
  }
  let output;
  if(cmd==="audit" || cmd==="verify"){
    output=await auditSource();
    if(withPython){
      // Fixed repo-controlled script and arguments only; no shell, no arbitrary program.
      const script=resolve(repoRoot,"tools/machineDebianSnapshot.py");
      const child=spawnSync("python3",[script],{
        cwd:repoRoot, shell:false, encoding:"utf8", timeout:10000,
        maxBuffer:65536, env:{
          PATH:process.env.PATH||"/usr/bin:/bin",PYTHONDONTWRITEBYTECODE:"1"
        }
      });
      if(child.error || child.status!==0) throw new Error("PYTHON_RECEIPT_FAILED");
      const py=JSON.parse(child.stdout);
      if(py.verdict!=="AMBER_SOURCE_ONLY" || py.mode!=="source" ||
         py.matrixCells!==16 || py.crownStatus!=="STOP" ||
         py.kernelModified!==false || py.physicalDeviceVerified!==false ||
         py.sql?.db!=="SQLITE_MEMORY_STRICT") throw new Error("PYTHON_RECEIPT_AUTHORITY");
      output.pythonSqlInterop="SOURCE_ONLY_VERIFIED";
      output.pythonReceiptSha256=py.contractSha256;
    }
    if(withDevice){
      const registry=JSON.parse(await readFile(resolve(repoRoot,"doctrine/deviceCapabilityRegistryV1.json"),"utf8"));
      checkRegistry(registry);
      // Synthetic approved fixture only, never a private asset or actual RSS observation.
      const fixture=encodePacket("LuHm ✦ 優先 3D", {registryHex:"0x0B", rssBytes:8388608});
      if(decodePacket(fixture).value!=="LuHm ✦ 優先 3D")throw new Error("JS_DEVICE_PARITY");
      const checked=spawnSync("python3",[resolve(repoRoot,"tools/deviceRegistrySqlReceipt.py")],{
        cwd:repoRoot, input:JSON.stringify(fixture), shell:false, encoding:"utf8",
        timeout:10000, maxBuffer:16384,
        env:{PATH:process.env.PATH||"/usr/bin:/bin",PYTHONDONTWRITEBYTECODE:"1"}
      });
      if(checked.error||checked.status!==0)throw new Error("PYTHON_DEVICE_PARITY");
      const result=JSON.parse(checked.stdout);
      if(result.status!=="AMBER_SOURCE_ONLY"||result.sqlite!=="IN_MEMORY_STRICT"||
         result.hex!==fixture.registryHex||result.byteCount!==fixture.byteCount||
         result.sha256!==fixture.sha256||result.rssBytes!==fixture.rssBytes||
         result.sqlServiceStarted!==false||result.deviceVerified!==false||
         result.crownStatus!=="STOP")throw new Error("DEVICE_RECEIPT_AUTHORITY");
      output.deviceRegistryInterop="SYNTHETIC_4X4_JS_PYTHON_SQL_VERIFIED";
      output.deviceRegistryHex=result.hex;
      output.devicePacketBytes=result.byteCount;
      output.deviceRssSample="SYNTHETIC_NOT_MEASURED";
    }
  }else if(cmd==="plan"){
    if(task===null) throw new Error("TASK_REQUIRED");
    const {policy,policySha256}=await loadPolicy();
    output=planTask(task,policy,policySha256);
  }else{
    const {policy}=await loadPolicy();
    output=remotePlan(policy);
  }
  process.stdout.write(JSON.stringify(output,null,2)+"\n");
}
main().catch(error=>fail(error?.message||"FAILED"));
