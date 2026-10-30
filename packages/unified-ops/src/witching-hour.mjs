/** Pure presentation state; never grants execution or release authority. */
export function witchingHour({mode="normal", sceneApproved=false, evidence="UNKNOWN"}={}) {
  if (!["normal","roleplay","company","art"].includes(mode)) throw new Error("UNKNOWN_MODE");
  const entered = mode !== "normal" && sceneApproved === true;
  return Object.freeze({schema:"luhmOs.witchingHour.v1", mode:entered?mode:"normal",
    evidence, mutationAllowed:false, releaseAllowed:false, activeAgents:0});
}
