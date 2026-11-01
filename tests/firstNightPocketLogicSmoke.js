#!/usr/bin/env node
// No packages or browser driver required: exercise the real inline HTML application script.
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const root = path.resolve(__dirname,"..");
const html = fs.readFileSync(path.join(root,"labs/first-night-pocket/index.html"),"utf8");
const quest = JSON.parse(fs.readFileSync(path.join(root,"game/story/firstNightQuest.json"),"utf8"));
const embeddedMatch = html.match(/<script type="application\/json" id="questData">([\s\S]*?)<\/script>/);
assert.ok(embeddedMatch,"canonical quest data must be embedded");
const data = JSON.parse(embeddedMatch[1]);
assert.equal(data.schema,quest.schema);
assert.equal(data.questId,quest.questId);
assert.deepEqual(data.steps,quest.steps.map(function(s){
  return Object.fromEntries(["stepId","worldId","event","objective","prompt","response"].map(function(k){return [k,s[k]];}));
}));
assert.deepEqual(data.completion,quest.completion);
assert.ok(html.includes('name="viewport"') && html.includes("prefers-reduced-motion"));
assert.ok(!/<script[^>]+src=/i.test(html) && !/<link[^>]+href=/i.test(html),"must be self-contained");
assert.ok(!/\bfetch\s*\(|\bXMLHttpRequest\b|\blocalStorage\b/.test(html),"no network or autosave");
const appMatch=html.match(/<script>\s*([\s\S]*?)<\/script>\s*<\/body>/i);
assert.ok(appMatch,"inline JS must exist");
new vm.Script(appMatch[1],{filename:"first-night-pocket.js"});
const elements = new Map();
const changes=[];
const locations=["neonRiverwalk","lumCoffeeHouse","cathedral"].map(function(id){
  return {getAttribute:function(){return id;},style:{display:""}};
});
function element(id){
  if(elements.has(id))return elements.get(id);
  let item={id,textContent:"",hidden:id==="sceneEditor",value:"",checked:true,
    style:{width:""},dataset:{palette:"violet"},listeners:{},attrs:{},
    classList:{toggle:function(label,value){changes.push([label,value]);}},
    addEventListener:function(name,fn){this.listeners[name]=fn;},
    setAttribute:function(k,v){this.attrs[k]=v;},
    querySelectorAll:function(){return locations;},
    scrollIntoView:function(){},focus:function(){},remove:function(){},
    click:function(){if(this.listeners.click)this.listeners.click.call(this);}};
  elements.set(id,item);return item;
}
element("questData").textContent=embeddedMatch[1];
const downloads=[];
const document={
  getElementById:element,
  createElement:function(){return {click:function(){downloads.push([this.href,this.download]);},remove:function(){}};},
  body:{appendChild:function(){}},
  addEventListener:function(name,fn){this[name]=fn;}
};
const sandbox={document,JSON,Object,String,Blob,URL:{createObjectURL:function(){return "blob:offline";},revokeObjectURL:function(){}},setTimeout:function(f){f();}};
vm.createContext(sandbox);
vm.runInContext(appMatch[1],sandbox);
assert.equal(element("questIndex").textContent,"STEP 1 OF 5");
assert.equal(element("objective").textContent,quest.steps[0].objective);
element("actionButton").click();
assert.equal(element("dialogueText").textContent,quest.steps[0].response);
element("actionButton").click();
assert.equal(element("questIndex").textContent,"STEP 2 OF 5");
for(let i=0;i<8;i++)element("actionButton").click();
assert.equal(element("questIndex").textContent,"CIRCUIT COMPLETE");
assert.equal(element("dialogueText").textContent,quest.completion.message);
element("restartButton").click();
assert.equal(element("questIndex").textContent,"STEP 1 OF 5");
element("editButton").click();
assert.equal(element("sceneEditor").hidden,false);
element("palette").value="cyan";
element("palette").listeners.change.call(element("palette"));
assert.equal(element("world").dataset.palette,"cyan");
element("stars").checked=false;
element("stars").listeners.change.call(element("stars"));
assert.deepEqual(changes[changes.length-1],["hideStars",true]);
element("directorNote").value="One new violet lamp";
element("exportButton").click();
assert.equal(downloads.length,1);
assert.equal(downloads[0][1],"first-night-scene-draft.json");
assert.equal(element("toast").textContent.includes("Nothing was uploaded."),true);
console.log("FIRST_NIGHT_POCKET_GREEN: 5 canon beats, restart, palette, manual export; no external runtime");
