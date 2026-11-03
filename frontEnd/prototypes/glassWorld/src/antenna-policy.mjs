/* Public wire contract only. No credentials, automatic execution or remote fetch. */
export const profiles = Object.freeze({
  antenna: Object.freeze({local3d:false, localInference:false, autoplay:false, execution:"remote"}),
  light: Object.freeze({local3d:"optIn", localInference:false, autoplay:false, execution:"remotePreferred"})
});
export function endpointUrl(value) {
  const url = new URL(value);
  const loopback = ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname);
  if ((url.protocol !== "https:" && !(loopback && url.protocol === "http:")) ||
      url.username || url.password || url.search || url.hash) throw Error("Use HTTPS without credentials, query or fragment; HTTP is loopback-only.");
  return url.href;
}
export function widgetIntent(action, target, requestId) {
  if (!["inspectCapabilities", "openMedia", "openGodot", "inspectJob"].includes(action)) throw Error("Unknown action");
  if (!["tablet", "raspberryPi", "remoteStudio"].includes(target)) throw Error("Unknown target");
  if (typeof requestId !== "string" || !/^[a-zA-Z0-9-]{1,64}$/.test(requestId)) throw Error("Invalid request identity");
  return Object.freeze({schema:"luhmOs.antennaIntent.v1", requestId, action, target,
    encoding:"json", authority:"requestOnly", executionProof:false});
}
