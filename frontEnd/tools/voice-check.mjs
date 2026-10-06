import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import vm from "node:vm";

const source = await readFile(new URL("../jquery/luhm.voiceCabinet.js", import.meta.url), "utf8");
const jquery = { fn: {} };
vm.runInNewContext(source, { window: { jQuery: jquery }, jQuery: jquery });

const cabinet = jquery.luhmVoiceCabinet;
assert.equal(cabinet.speechRecognitionConstructor({ SpeechRecognition: function Standard() {} }).name, "Standard", "supports standard browser recognition");
assert.equal(cabinet.speechRecognitionConstructor({ webkitSpeechRecognition: function Prefixed() {} }).name, "Prefixed", "supports prefixed WebView recognition");
assert.equal(cabinet.speechRecognitionConstructor({}), null, "gracefully handles hosts without recognition");
assert.equal(cabinet.transcriptFromResult({ results: [[{ transcript: " hello " }]] }), "hello", "extracts a speech result");
assert.equal(cabinet.transcriptFromResult({ results: [[{ transcript: "x".repeat(1300) }]] }).length, 1200, "bounds recognized input");
assert.equal(cabinet.parseCommand("C", "OUTSIDE"), null, "C stays literal outside After Hours");
assert.equal(cabinet.parseCommand("AFTER HOURS", "OUTSIDE"), "enter", "entry is explicit");
assert.equal(cabinet.parseCommand("C", "ACTIVE"), "continue", "C advances an active scene");
assert.equal(cabinet.parseCommand("OOC", "ACTIVE"), "pause", "OOC pauses the scene");
assert.equal(cabinet.parseCommand("C", "PAUSED"), "continueWhilePaused", "paused scenes require resume");
assert.equal(cabinet.parseCommand("RESUME", "PAUSED"), "resume", "resume is explicit");
assert.equal(cabinet.parseCommand("EXIT", "ACTIVE"), "exit", "exit closes the scene");

const validTurn = cabinet.normalizeTurn({
  kind: "namedEnsembleTurn",
  speakerSegments: [
    { speakerId: "lum", utterance: "The scene is ready." },
    { speakerId: "urdDoctorGoddess", text: "Keep it classy." }
  ]
});
assert.equal(validTurn.speakerSegments.length, 2, "keeps named speaker segments");
assert.equal(validTurn.speakerSegments[0].speakerId, "lum", "preserves canonical speaker identity");
assert.equal(cabinet.normalizeTurn({ kind: "namedEnsembleTurn", speakerSegments: [{ speakerId: "root", text: "<script>" }] }), null,
  "rejects unknown speaker identities");
assert.equal(cabinet.normalizeTurn({ kind: "rawTranscript", speakerSegments: [{ speakerId: "lum", text: "hello" }] }), null,
  "rejects untyped response payloads");
assert.equal(cabinet.normalizeTurn({ kind: "namedEnsembleTurn", speakerSegments: [{ speakerId: "lum", text: "x".repeat(1200) }] }).speakerSegments[0].text.length, 900,
  "bounds each spoken segment");

console.log("GREEN After Hours command and speaker-segment checks");
