"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const studio = require("../host/harness/studioDeck.js");
const root = path.resolve(__dirname, "..");
const contract = JSON.parse(fs.readFileSync(path.join(root, "doctrine/localMediaDeckV1.json"), "utf8"));
const markup = fs.readFileSync(path.join(root, "host/harness/studioDeck.html"), "utf8");
const js = fs.readFileSync(path.join(root, "host/harness/studioDeck.js"), "utf8");

test("source-only profile does not assert VLC or device runtime", () => {
  assert.equal(contract.status, "PROPOSED_SOURCE_TESTING");
  assert.equal(contract.vlc.browserVlcPlugin, false);
  assert.equal(contract.vlc.rawHttpPort, false);
  assert.equal(contract.vlc.bundledAndroidLibVlc, false);
  assert.equal(contract.backend.mediaUpload, false);
  assert.equal(contract.promotion, false);
  assert.equal(contract.crownStatus, "STOP");
});
test("media preview nodes and native seek/transport controls exist", () => {
  for (const id of ["studioLocalMediaInput","studioLocalMediaStop","studioLocalMediaStatus","studioLocalVideo","studioLocalAudio"])
    assert.ok(markup.includes('id="' + id + '"'), id);
  assert.match(markup, /<video[^>]+controls[^>]+playsinline[^>]+preload="metadata"/);
  assert.match(markup, /<audio[^>]+controls[^>]+preload="metadata"/);
  assert.doesNotMatch(markup, /(?:autoplay|vlc:\/\/|:8080)/i);
  assert.match(js, /URL\.revokeObjectURL\(activeUrl\)/);
  assert.match(js, /addEventListener\("pagehide", clear/);
  assert.match(js, /wireLocalMediaDeck\(doc\)/);
});
test("permitted file selects native decoder with bounded size", () => {
  assert.deepEqual(studio.localMediaCapability({name:"original.mp4",type:"video/mp4",size:1024}), {ok:true,mime:"video/mp4",kind:"video"});
  assert.deepEqual(studio.localMediaCapability({name:"sound.mp3",type:"audio/mpeg",size:10}), {ok:true,mime:"audio/mpeg",kind:"audio"});
  assert.equal(studio.localMediaCapability({name:"clip.webm",type:"",size:100}).ok, true);
});
test("rejects mismatches, remote-shaped strings, unknown formats and oversized files", () => {
  for (const file of [
    {name:"video.mp4",type:"text/html",size:128},
    {name:"video.mkv",type:"video/x-matroska",size:1024},
    {name:"https://invalid/video.mp4?x=1",type:"video/mp4",size:1},
    {name:"video.mp4",type:"video/mp4",size:268435457},
    {name:"video.mp4",type:"video/mp4",size:0},
    {name:"video.mp4",type:"video/mp4",size:-1},
    {name:"video.mp4",type:"video/mp4",size:NaN},
  ]) assert.equal(studio.localMediaCapability(file).ok,false);
});
test("no standalone VLC server or shell invocation is added to DOM adapter", () => {
  assert.doesNotMatch(js,/localhost:8080|127\.0\.0\.1:8080|python-vlc|child_process|exec\(/i);
  assert.doesNotMatch(markup, /<object\b|<embed\b|<script[^>]+src="https?:/i);
});
