/* LuHm-OS local GLB intake: no fetch, no uploads, strict embedded-resource policy. */
export const MAX_LUM_GLB_BYTES = 20 * 1024 * 1024;
const reject = code => { throw new Error(code); };
export async function inspectLocalGlb(file) {
  if (!file || typeof file.name !== "string" || !/\.glb$/i.test(file.name) ||
      !Number.isSafeInteger(file.size) || file.size < 28 || file.size > MAX_LUM_GLB_BYTES ||
      typeof file.slice !== "function") reject("RED_GLB_SIZE_OR_TYPE");
  const head = new DataView(await file.slice(0, 20).arrayBuffer());
  if (head.getUint32(0, true) !== 0x46546c67 || head.getUint32(4, true) !== 2 ||
      head.getUint32(8, true) !== file.size ||
      head.getUint32(16, true) !== 0x4e4f534a) reject("RED_GLB_HEADER");
  const jsonLength = head.getUint32(12, true);
  if (jsonLength < 2 || jsonLength > 1024 * 1024 ||
      jsonLength % 4 !== 0 || 20 + jsonLength > file.size) reject("RED_GLB_JSON_BOUNDS");
  let metadata;
  try {
    const buffer = await file.slice(20, 20 + jsonLength).arrayBuffer();
    metadata = JSON.parse(new TextDecoder("utf-8", { fatal:true }).decode(buffer));
  } catch { reject("RED_GLB_JSON"); }
  if (metadata?.asset?.version !== "2.0" ||
      !Array.isArray(metadata.nodes) || metadata.nodes.length > 1000 ||
      !Array.isArray(metadata.meshes) || metadata.meshes.length > 100 ||
      (metadata.animations?.length ?? 0) > 24 ||
      (metadata.images?.length ?? 0) > 100) reject("RED_GLB_COMPLEXITY");
  // This intake accepts self-contained .glb only, so even an otherwise-valid
  // glTF reference cannot silently fetch external resources.
  for (const item of [...(metadata.buffers || []), ...(metadata.images || []), ...(metadata.shaders || [])]) {
    if (item?.uri !== undefined) reject("RED_EXTERNAL_GLB_URI");
  }
  const unsupported = new Set(["KHR_draco_mesh_compression","EXT_meshopt_compression","KHR_texture_basisu"]);
  if ((metadata.extensionsRequired || []).some(ext => unsupported.has(ext))) reject("RED_GLB_UNSUPPORTED_CODEC");
  return Object.freeze({
    fileName:file.name,
    meshes:metadata.meshes.length,
    nodes:metadata.nodes.length,
    animations:metadata.animations?.length ?? 0,
    animationNames:(metadata.animations || []).map((a,i) => String(a.name || ("Clip " + (i+1))).slice(0,80)),
    embeddedOnly:true
  });
}
