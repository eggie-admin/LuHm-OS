/* Source-only renderer budget. This does not enable Vulkan or native device privileges. */
export function chooseRenderPolicy({webGlVersion,coarsePointer=false,reducedMotion=false}={}) {
  const webGl2=webGlVersion===2;
  const conservative=Boolean(coarsePointer || reducedMotion);
  return Object.freeze({
    renderer:webGl2?"WEBGL2":"WEBGL1_FALLBACK",
    nativeVulkan:false,
    maxPixelRatio:conservative?1.25:1.6,
    shadowMapSize:webGl2?(conservative?512:1024):0,
    defaultShadows:webGl2 && !reducedMotion
  });
}
