/** LuHm machine-to-AI local audit. Standard-library only; no network or runtime model. */
import { readFile, lstat, realpath } from "node:fs/promises";
import { createHash } from "node:crypto";
import { resolve, sep, dirname } from "node:path";
import { fileURLToPath } from "node:url";

export const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
export const policyFile = "doctrine/machineLocalAgentAuditV1.json";
export const DOMAINS = Object.freeze(["kernel", "data", "browser", "agent"]);
export const PHASES = Object.freeze(["detect", "bound", "test", "escalate"]);
export const ACTIONS = Object.freeze(["audit", "plan", "verify", "remote-plan"]);
export const HEX16 = Object.freeze(Array.from({length:16},(_,i)=>"0x"+i.toString(16).toUpperCase().padStart(2,"0")));
const EXPECTED_BROWSER = ["firefox","chromium","samsungInternet","safari"];
const EXPECTED_SERVICES = ["pipewire","pulseaudio","vulkan","sqlite","nginx","apache2","php","postgres","mariadb","ffmpeg","babylon","vue","jquery"];
const SOURCE_ROOTS = ["doctrine/",".devcontainer/","host/","tools/","infra/"];
const SHA256 = /^[a-f0-9]{64}$/;
const MAX_BYTES = 1_048_576;
const TASK_LIMIT = 1024;
const REQUIRED_FALSE = ["remoteEnabled","networkRequestsAllowed","modelInferenceIncluded",
  "autonomousAgentActivation","downloadRemoteAssets","writeHostKernel","writeUserFiles",
  "rootPrivilege","runSqlServer","installSystemPackages","publicDeploy","providerSecretsIncluded"];

function need(ok, code) { if(!ok) throw new Error(code); }
function sha(buffer) { return createHash("sha256").update(buffer).digest("hex"); }
function cleanRelative(path) {
  need(typeof path === "string" && path.length > 0 && path.length < 180 && !path.includes("\\")
    && !path.includes("\0") && !path.startsWith("/") && !path.split("/").includes("..")
    && SOURCE_ROOTS.some(prefix=>path.startsWith(prefix)), "RED_SOURCE_PATH");
  return path;
}
async function bytesFromFile(root, relative) {
  cleanRelative(relative);
  const base = await realpath(root);
  const file = resolve(base,relative);
  need(file.startsWith(base+sep), "RED_SOURCE_ESCAPE");
  const stat = await lstat(file);
  need(stat.isFile() && !stat.isSymbolicLink() && stat.size > 0 && stat.size <= MAX_BYTES,
       "RED_SOURCE_FILE");
  need((await realpath(file)) === file, "RED_SOURCE_SYMLINK");
  const content = await readFile(file);
  need(content.byteLength === stat.size && content.byteLength <= MAX_BYTES, "RED_SOURCE_RACE");
  return content;
}
export async function loadPolicy(root=repoRoot) {
  const content = await bytesFromFile(root, policyFile);
  const policy = JSON.parse(content.toString("utf8"));
  return {policy, policySha256:sha(content)};
}
export function checkPolicy(p) {
  need(p && typeof p === "object" && !Array.isArray(p) &&
       p.schema === "luhmOs.machineLocalAgentAudit.v1" &&
       p.status === "PROPOSED_SOURCE_ONLY" && p.crownStatus === "STOP" &&
       p.authority === "Professor", "RED_POLICY_AUTHORITY");
  need(p.sourceLaw === "AI proposes. Policy authorizes. CI proves. Human promotes.",
       "RED_SOURCE_LAW");
  need(JSON.stringify(p.domains?.map(x=>x.id)) === JSON.stringify(DOMAINS) &&
       JSON.stringify(p.phases) === JSON.stringify(PHASES), "RED_4X4_AXES");
  need(Array.isArray(p.matrix) && p.matrix.length === 16, "RED_4X4_LENGTH");
  for(let i=0;i<16;i++){
    const c=p.matrix[i];
    need(c && c.index===i && c.hex===HEX16[i] && c.domain===DOMAINS[Math.floor(i/4)] &&
         c.phase===PHASES[i%4] && c.proof==="SOURCE_ONLY" && c.hardwareVerified===false,
         "RED_HEX_OR_PROOF");
  }
  need(JSON.stringify(p.browserTargets?.map(x=>x.id))===JSON.stringify(EXPECTED_BROWSER) &&
       JSON.stringify(p.softwareDecisions?.map(x=>x.id))===JSON.stringify(EXPECTED_SERVICES),
       "RED_BROWSER_OR_VENDOR");
  for(const [id,denied] of [["nginx","OPTIONAL_EDGE_ONLY"],["apache2","EXCLUDE_BY_DEFAULT"],
    ["php","EXCLUDE_BY_DEFAULT"],["postgres","EXCLUDE_BY_DEFAULT"],
    ["mariadb","EXCLUDE_BY_DEFAULT"],["vulkan","HOST_DRIVER_ONLY_NOT_CONTAINER_INSTALL"]]){
    need(p.softwareDecisions.find(x=>x.id===id)?.policy===denied,"RED_UNAUTHORIZED_VENDOR");
  }
  need(JSON.stringify(p.allowedLocalActions)===JSON.stringify(ACTIONS), "RED_LOCAL_ACTIONS");
  need(p.limits?.maxTaskUtf8Bytes===TASK_LIMIT && p.limits?.maxSourceBytes===MAX_BYTES &&
       p.limits.maxSources<=16 && p.limits.maxAgentPlanSteps===4 &&
       p.limits.maxReceiptBytes<=65536 &&
       REQUIRED_FALSE.every(k=>p.limits[k]===false), "RED_LOCAL_PRIVILEGE");
  need(p.remoteBoundary?.mode==="DRY_RUN_ONLY" && Array.isArray(p.remoteBoundary.allowedEndpoints) &&
       p.remoteBoundary.allowedEndpoints.length===0 &&
       p.remoteBoundary.directDatabasePort===false &&
       p.remoteBoundary.providerCostsMustBeApproved===true &&
       p.remoteBoundary.requires?.includes("ownerAuthorization") &&
       p.remoteBoundary.requires.includes("authenticatedTransport") &&
       p.remoteBoundary.requires.includes("signedCapabilityReceipt"), "RED_REMOTE_AUTHORITY");
  need(Array.isArray(p.sourceScope) && p.sourceScope.length<=p.limits.maxSources &&
       p.sourceScope.length>=6 && new Set(p.sourceScope).size===p.sourceScope.length &&
       p.sourceScope.every(x=>{try{cleanRelative(x);return true;}catch{return false;}}),
       "RED_SOURCE_INVENTORY");
  need(Array.isArray(p.taskIntents) && p.taskIntents.length===4 &&
       p.taskIntents.every(x=>Array.isArray(x.labels)&&x.labels.length>0 &&
       x.output==="LOCAL_PLAN_ONLY"&&x.next), "RED_AGENT_INTENTS");
  need(Array.isArray(p.nextGates) && p.nextGates.length>=6 &&
       p.nextGates.at(-1)==="humanReleaseApproval", "RED_PROMOTION_GATES");
  need(Array.isArray(p.upstream) && p.upstream.length>=8 &&
       p.upstream.every(x=>URL.canParse(x.url) && new URL(x.url).protocol==="https:" &&
       !new URL(x.url).username && !new URL(x.url).password), "RED_UPSTREAM_REFS");
  return true;
}
export function classifyTask(task,policy) {
  need(typeof task==="string" && task.trim().length>0 &&
       new TextEncoder().encode(task).length<=TASK_LIMIT &&
       !/[\u0000-\u0008\u000B-\u001F]/u.test(task), "RED_TASK_UTF8_BUDGET");
  const normalized=task.normalize("NFKC").toLowerCase();
  const matches=policy.taskIntents.filter(item=>
    item.labels.some(label=>new RegExp("(^|[^\\p{L}\\p{N}])"+label+"(?=$|[^\\p{L}\\p{N}])","u").test(normalized)));
  return matches.length ? matches[0] : null;
}
export function planTask(task, policy, receiptSha256="UNKNOWN"){
  checkPolicy(policy);
  const match=classifyTask(task,policy);
  const intent=match?.id??"unknown";
  const next=match?.next??"manualClassification";
  const steps=["classifyInput","bindCurrentSource","proposeReadOnlyCheck","humanReview"];
  need(steps.length<=policy.limits.maxAgentPlanSteps, "RED_PLAN_CAP");
  return {schema:"luhmOs.localAgentPlan.v1",intent,
    taskBytes:new TextEncoder().encode(task).length,sourceReceiptSha256:receiptSha256,
    steps,output:"LOCAL_PLAN_ONLY",nextGate:next,modelInferenceUsed:false,
    agentActivated:false,commandsExecuted:false,authority:"PROPOSE_ONLY",crownStatus:"STOP"};
}
export async function auditSource(root=repoRoot){
  const {policy,policySha256}=await loadPolicy(root);
  checkPolicy(policy);
  const files=[];
  for (const path of policy.sourceScope){
    const bytes=await bytesFromFile(root,path);
    files.push({path,bytes:bytes.byteLength,sha256:sha(bytes)});
  }
  const receipt={schema:"luhmOs.machineLocalAuditReceipt.v1",
    verdict:"AMBER_SOURCE_ONLY",matrixCells:16,hex:HEX16,
    sourceContractSha256:policySha256,sources:files,
    browsers:policy.browserTargets.map(x=>({id:x.id,proof:"NOT_PHYSICALLY_TESTED"})),
    vendorDecisions:policy.softwareDecisions.map(x=>({id:x.id,policy:x.policy})),
    npmRuntimeDependencies:0,localActions:ACTIONS,pythonSqlInterop:"SEPARATE_GATE",
    hardwareVerified:false,pipewireActive:"UNKNOWN",vulkanActive:"UNKNOWN",
    aiModelAvailable:"UNKNOWN",modelInferenceUsed:false,agentActivated:false,
    networkAccessed:false,remoteInvocation:"DISABLED",
    kernelChanged:false,filesChanged:false,publicServerStarted:false,crownStatus:"STOP"};
  need(Buffer.byteLength(JSON.stringify(receipt),"utf8")<=policy.limits.maxReceiptBytes,
       "RED_RECEIPT_BUDGET");
  return receipt;
}
export function remotePlan(policy){
  checkPolicy(policy);
  return {schema:"luhmOs.remoteAuditHandoff.v1",status:"BLOCKED_PENDING_APPROVAL",
    proposedRoute:"localVerifiedReceipt → authenticated approved HTTPS origin → remote worker",
    requirements:policy.remoteBoundary.requires,networkRequestMade:false,
    remoteOriginConfigured:false,modelCalled:false,modelInferenceIncluded:false,
    secretsRead:false,receiptPromotion:false,crownStatus:"STOP"};
}
