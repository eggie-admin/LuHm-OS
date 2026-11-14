/* Shared npm/widget/runtime data contract. No engine, provider or asset imports. */
export const antennaBudget = Object.freeze({
  basis:"provisionalProjectBudgetNotHostLimit", totalBytes:12500000,
  widgetBytes:262144, modelBytesInWidget:0, base64Assets:false
});
export function animationRequest(action,clip="",time=0){
  if(!["play","pause","seek"].includes(action))throw Error("Unknown animation action");
  if(typeof clip!=="string"||clip.length>128||/[\u0000-\u001f]/.test(clip))throw Error("Invalid clip");
  if(action==="play"&&!clip)throw Error("Choose an imported clip");
  if(typeof time!=="number"||!Number.isFinite(time)||time<0||time>3600)throw Error("Invalid timeline time");
  return Object.freeze({schema:"luhmOs.avatarAnimation.v1",action,clip,time});
}
