/* LuHm-OS: Project Premonition | local HTML5 preview, optional native VLC outside browser.
 * No uploads, network URLs, VLC HTTP credentials, or autosave.
 */
import $ from "jquery";
const videoTypes = new Set(["video/mp4","video/webm"]);
const audioTypes = new Set(["audio/mpeg","audio/mp3","audio/wav","audio/x-wav","audio/ogg","audio/mp4"]);
const maxBytes = 700 * 1024 * 1024;
const allowed = {".mp4":"video", ".webm":"video", ".mp3":"audio", ".wav":"audio", ".ogg":"audio", ".m4a":"audio"};
export function classifyLocalMedia(file) {
  if (!file || typeof file.name !== "string" || typeof file.size !== "number"
      || file.size < 1 || file.size > maxBytes) throw Error("RED_MEDIA_FILE");
  const ext = "." + (file.name.split(".").at(-1) || "").toLowerCase();
  const kind = allowed[ext];
  const mime = String(file.type || "").toLowerCase();
  if (!kind || (mime && !(kind === "video" ? videoTypes : audioTypes).has(mime))) {
    throw Error("RED_MEDIA_TYPE");
  }
  return { kind, sizeBytes: file.size, extension:ext };
}
export function mountLocalMediaDeck(root) {
  const picker = root.querySelector('[data-luhm-media-file]');
  const video = root.querySelector('[data-luhm-media-video]');
  const audio = root.querySelector('[data-luhm-media-audio]');
  const status = root.querySelector('[data-luhm-media-status]');
  if (!picker || !video || !audio || !status) throw Error("RED_MEDIA_DECK_DOM");
  let blobUrl = null;
  let current = null;
  const unbind = () => {
    for (const element of [video, audio]) {
      element.pause();
      element.removeAttribute("src");
      element.load();
      element.hidden = true;
    }
    if (blobUrl) URL.revokeObjectURL(blobUrl);
    blobUrl = null;
    current = null;
  };
  const onchange = () => {
    unbind();
    const file = picker.files?.[0];
    if (!file) { status.textContent = "Choose a local MP4 or audio file."; return; }
    try {
      const record = classifyLocalMedia(file);
      blobUrl = URL.createObjectURL(file);
      current = record.kind === "video" ? video : audio;
      current.src = blobUrl;
      current.hidden = false;
      current.controls = true;
      status.textContent = "Private local "+record.kind+" ready. Playback starts only when you press play.";
      $(root).trigger("luhm:media:preview", [{
        schema:"luhmOs.localMediaPreviewIntent.v1", product:"LuHm-OS",
        kind:record.kind, sizeBytes:record.sizeBytes, extension:record.extension,
        source:"localFilePicker", pythonValidationRequired:true,
        networkUpload:false, releasePublished:false, crownGranted:false
      }]);
    } catch {
      status.textContent = "Unsupported file or size. No media was opened.";
      picker.value = "";
    }
  };
  picker.addEventListener("change", onchange);
  const leave = () => { picker.removeEventListener("change", onchange); unbind(); };
  window.addEventListener("pagehide", leave, {once:true});
  return leave;
}
