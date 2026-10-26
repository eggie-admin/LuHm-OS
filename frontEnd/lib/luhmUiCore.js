/* LuHm OS original UI core, source-only candidate.
 * Pure string parsing and timer policy; no browser network, SQL, tokens, DOM,
 * provider invocation, roleplay authority or agent activation.
 * Compatible with classic script tags and Node CI without bundler.
 */
(function (root, createCore) {
  "use strict";
  const core = createCore();
  if (typeof module === "object" && module.exports) module.exports = core;
  if (root) root.LuHmUiCore = core;
}(typeof window === "object" ? window : undefined, function () {
  "use strict";
  const vendorAliases = Object.freeze({
    "OPENAI": "openAi",
    "OPEN DADDY": "openAi",
    "OPENDADDY": "openAi",
    "GOOGLE": "googleAi",
    "GOOGLE AI": "googleAi",
    "BIG BROTHER": "googleAi",
    "BIGBROTHER": "googleAi",
    "COPILOT": "githubCopilot",
    "GITHUB": "githubCopilot",
    "GITHUB COPILOT": "githubCopilot",
    "HUGGINGFACE": "huggingFace",
    "HUGGING FACE": "huggingFace",
    "HF": "huggingFace",
    "EDGE": "edgeGallery",
    "EDGE GALLERY": "edgeGallery",
    "EDGEGALLERY": "edgeGallery"
  });

  // Recognize both registered phrases. Merely parsing words cannot authorize.
  function normalizeMagicText(value) {
    return String(value || "")
      .normalize("NFC")
      .toLocaleLowerCase("en-US")
      .replace(/[^\p{L}\p{N}]+/gu, " ")
      .trim()
      .replace(/\s+/gu, " ");
  }

  function matchesMagicTrigger(value) {
    const normalized = " " + normalizeMagicText(value) + " ";
    const oldMagicPhrase = " i invoke the old magic ";
    const writtenDonePhrase = " so let it be written so let it be done ";
    return normalized.includes(oldMagicPhrase) &&
      normalized.includes(writtenDonePhrase);
  }

  function normalizeDebugCommand(value) {
    return String(value || "")
      .normalize("NFC")
      .toUpperCase()
      .replace(/[^A-Z0-9]+/g, " ")
      .trim()
      .replace(/\s+/g, " ");
  }

  function parseVendorDebugCommand(value) {
    const command = normalizeDebugCommand(value);
    if (command === "VENDOR DEBUG" || command === "DEBUG VENDOR") {
      return { providerId: "all", command: command };
    }
    let providerText = "";
    if (command.startsWith("VENDOR DEBUG ")) providerText = command.slice(13);
    if (command.startsWith("DEBUG VENDOR ")) providerText = command.slice(13);
    if (command.startsWith("DEBUG ") && !providerText) providerText = command.slice(6);
    const providerId = vendorAliases[providerText];
    return providerId ? { providerId: providerId, command: command } : null;
  }

  function clockIntervalMs(value) {
    const configured = Number(value);
    if (!Number.isFinite(configured) || configured <= 0) return 30000;
    return Math.max(15000, Math.min(configured, 120000));
  }

  return Object.freeze({
    schema: "luhmOs.uiCore.v1",
    normalizeMagicText: normalizeMagicText,
    matchesMagicTrigger: matchesMagicTrigger,
    normalizeDebugCommand: normalizeDebugCommand,
    parseVendorDebugCommand: parseVendorDebugCommand,
    clockIntervalMs: clockIntervalMs
  });
}));
