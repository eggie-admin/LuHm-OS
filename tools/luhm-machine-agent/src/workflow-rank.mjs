/** Universal session-only action sorting, no telemetry or persistence. */
export const orderedActions=Object.freeze(["play","edit","assets","build","audit","settings"]);
function need(v,code){if(!v)throw new Error("RED_"+code);}
const isUInt=v=>typeof v==="number"&&Number.isSafeInteger(v)&&v>=0;
export function initialCounts(){return Object.fromEntries(orderedActions.map(id=>[id,0]));}
export function sortActions(counts){
 need(counts&&typeof counts==="object"&&!Array.isArray(counts) &&
   Object.keys(counts).sort().join(",")===orderedActions.slice().sort().join(",") &&
   orderedActions.every(id=>isUInt(counts[id])&&counts[id]<=1_000_000),"GUI_COUNT_SHAPE");
 return orderedActions.slice().sort((a,b)=>
   counts[b]-counts[a] || orderedActions.indexOf(a)-orderedActions.indexOf(b));
}
export function selectAction(counts,id){
 sortActions(counts);
 need(orderedActions.includes(id),"GUI_ACTION_UNKNOWN");
 need(counts[id]<1_000_000,"GUI_COUNT_LIMIT");
 return {...counts,[id]:counts[id]+1};
}
