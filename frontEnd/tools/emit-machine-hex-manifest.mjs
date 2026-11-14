/** Synthetic CI transport fixture: JS candidate JSON -> Python validator.
 * Requires exact git source SHA passed by caller. No network, SQL or filesystem writes.
 */
import {buildLuHmHexCastManifest} from "../core/machineCastHexBridge.mjs";
const sha=process.argv[2];
if (!/^[0-9a-f]{40}$/.test(sha||"")) {
  throw new TypeError("RED_EXACT_SOURCE_REQUIRED");
}
process.stdout.write(JSON.stringify(buildLuHmHexCastManifest({
  sourceRef:sha,taskId:"machineCastReview",scopeId:"machineSql",
  beat:"hear",tier:"technologyFastPath"
}))+"\n");
