/** Capability-first AI proposal. No network calls or model claims. */
const CAPABILITIES = new Set(["reasoning","research","coding","art","verification"]);
export function aiPlan({capability, provider="openai", approved=false}={}) {
  if (!CAPABILITIES.has(capability)) throw new Error("UNKNOWN_CAPABILITY");
  if (!["openai","google","deterministicLocal"].includes(provider)) throw new Error("UNKNOWN_PROVIDER");
  return Object.freeze({schema:"luhmOs.aiPlan.v1", capability, provider,
    humanApproved:approved===true, modelExecutionProven:false,
    toolExecutionAllowed:false, output:"PROPOSAL_ONLY"});
}
