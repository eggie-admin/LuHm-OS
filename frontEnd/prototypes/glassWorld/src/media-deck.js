/* Local-only HTML5 media preview. Native VLC/libVLC is a SEPARATE, opt-in Android host.
 * No network URL, VLC browser plugin, file upload, remote CDN or auto-play.
 */
const videoTypes = new Set(["video/mp4", "video/webm"]);
const audioTypes = new Set(["audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/ogg", "audio/mp4"]);
const imageTypes = new Set(["image/webp", "image/png", "image/jpeg", "image/avif"]);
const videoMax = 700 * 1024 * 1024;
const imageMax = 24 * 1024 * 1024;
const allowed = Object.freeze({
  ".mp4": "video", ".webm": "video",
  ".mp3": "audio", ".wav": "audio", ".ogg": "audio", ".m4a": "audio",
  ".webp": "image", ".png": "image", ".jpg": "image", ".jpeg": "image", ".avif": "image"
});
export function classifyLocalMedia(file) {
  if (!file || typeof file.name !== "string" || !file.name || file.name.length > 128 ||
      /[\\/]/.test(file.name) || typeof file.size !== "number" || !Number.isSafeInteger(file.size)) {
    throw Error("RED_MEDIA_FILE");
  }
  const ext = "." + (file.name.split(".").at(-1) || "").toLowerCase();
  const kind = allowed[ext];
  if (!kind || file.size < 1 || file.size > (kind === "image" ? imageMax : videoMax)) {
    throw Error("RED_MEDIA_FILE");
  }
  const mime = String(file.type || "").toLowerCase();
  const types = kind === "video" ? videoTypes : kind === "audio" ? audioTypes : imageTypes;
  if (mime && !types.has(mime)) throw Error("RED_MEDIA_TYPE");
  if (kind === "image" && mime && ({
    ".webp":"image/webp", ".png":"image/png",
    ".jpg":"image/jpeg", ".jpeg":"image/jpeg", ".avif":"image/avif"
  })[ext] !== mime) throw Error("RED_MEDIA_TYPE");
  return { kind, sizeBytes: file.size, extension: ext };
}
export function mountLocalMediaDeck(root) {
  const picker = root.querySelector("[data-luhm-media-file]");
  const video = root.querySelector("[data-luhm-media-video]");
  const audio = root.querySelector("[data-luhm-media-audio]");
  const image = root.querySelector("[data-luhm-media-image]");
  const status = root.querySelector("[data-luhm-media-status]");
  if (!picker || !video || !audio || !image || !status) throw Error("RED_MEDIA_DECK_DOM");
  let blobUrl = null;
  function unbind() {
    for (const element of [video, audio, image]) {
      if (typeof element.pause === "function") element.pause();
      element.removeAttribute("src");
      if (typeof element.load === "function") element.load();
      element.hidden = true;
    }
    if (blobUrl) URL.revokeObjectURL(blobUrl);
    blobUrl = null;
  }
  const onchange = () => {
    unbind();
    const file = picker.files?.[0];
    if (!file) { status.textContent = "Choose local MP4, audio, or image. Nothing uploads."; return; }
    try {
      const record = classifyLocalMedia(file);
      blobUrl = URL.createObjectURL(file);
      const target = record.kind === "video" ? video : record.kind === "audio" ? audio : image;
      target.src = blobUrl;
      target.hidden = false;
      if (record.kind !== "image") target.controls = true;
      status.textContent = "Private local " + record.kind + " preview selected. No server upload.";
      root.dispatchEvent(new CustomEvent("luhm:media:preview", { detail: {
        schema: "luhmOs.localMediaPreviewIntent.v1", product: "LuHm-OS",
        kind: record.kind, sizeBytes: record.sizeBytes, extension: record.extension,
        source: "localFilePicker", pythonValidationRequired: true,
        networkUpload: false, releasePublished: false, crownGranted: false,
        nativeVlcRunning: false
      }, bubbles: false, composed: false }));
    } catch {
      status.textContent = "Unsupported local file or size. Nothing was opened.";
      picker.value = "";
    }
  };
  picker.addEventListener("change", onchange);
  const leave = () => { picker.removeEventListener("change", onchange); unbind(); };
  window.addEventListener("pagehide", leave, {once: true});
  return leave;
}
