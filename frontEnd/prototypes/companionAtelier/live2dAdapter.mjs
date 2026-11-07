/**
 * Cubism rendering is NOT bundled. This safe gate returns explicit requirements
 * before a separately licensed SDK and independently cleared model are wired.
 */
export function inspectLive2dCandidate(candidate) {
  if (!candidate || candidate.provenance !== "OWNER_AUTHORED_OR_LICENSED" || candidate.clearance !== "VERIFIED" ||
      candidate.modelFormat !== "cubism5" || candidate.modelManifest?.endsWith(".model3.json") !== true ||
      /[:\\]|(?:^|\/)\.\.?\//.test(candidate.modelManifest) ||
      !/^[A-Za-z0-9_./-]+$/.test(candidate.modelManifest)) {
    return Object.freeze({accepted:false,mode:"CSS_FALLBACK",reason:"NO_CLEAR_MODEL_OR_LICENSE"});
  }
  return Object.freeze({accepted:true,mode:"ADAPTER_NOT_INSTALLED",reason:"CUBISM_RUNTIME_LICENSE_AND_LOAD_NOT_VERIFIED"});
}
