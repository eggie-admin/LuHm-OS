#!/usr/bin/env node
/* Hash explicit local originals using bounded streaming; never extract or upload. */
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const {createHash} = require("node:crypto");
const {category,maxFiles} = require("../host/harness/studioDeck.js");
async function register(paths,sourceRef="UNKNOWN") {
  if (!paths.length || paths.length>maxFiles) throw Error("Provide 1 to 128 explicit file paths.");
  const assets=[],duplicates=[];
  for (const filename of paths) {
    const initial=fs.lstatSync(filename);
    if (!initial.isFile() || initial.isSymbolicLink()) throw Error("Only explicit regular files are accepted: "+filename);
    const handle=await fs.promises.open(filename,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);
    let stat,sha256;
    try {
      stat=await handle.stat();
      if(!stat.isFile()||stat.ino!==initial.ino||stat.dev!==initial.dev)throw Error("Source identity changed during intake.");
      const hash=createHash("sha256");
      for await (const chunk of handle.createReadStream({autoClose:false})) hash.update(chunk);
      const after=await handle.stat();
      if(after.size!==stat.size||after.mtimeMs!==stat.mtimeMs)throw Error("Source changed during fingerprinting.");
      sha256=hash.digest("hex");
    } finally {await handle.close();}
    if (assets.some(row=>row.sha256===sha256)) {duplicates.push(path.basename(filename));continue;}
    assets.push({originalName:path.basename(filename).slice(0,256),bytes:stat.size,mime:"application/octet-stream",category:category(filename),sha256,rights:"UNKNOWN",canon:"UNAPPROVED",lane:"needsReview"});
  }
  return {manifest:{schema:"luhmOs.assetRegister.v1",sourceRef,createdAt:new Date().toISOString(),serverWrites:false,productionPromotion:false,assets},duplicates};
}
module.exports={register};
if(require.main===module){
  const [output,...paths]=process.argv.slice(2);
  if(!output){console.error("Usage: node tools/registerStudioAssets.cjs NEW_OUTPUT.json ORIGINAL_FILE [...]");process.exitCode=1;}
  else register(paths,process.env.LUHM_SOURCE_REF||"UNKNOWN").then(({manifest,duplicates})=>{
    fs.writeFileSync(output,JSON.stringify(manifest,null,2)+"\n",{flag:"wx"});
    console.log(JSON.stringify({registered:manifest.assets.length,duplicates:duplicates.length,originalsChanged:false,archivesExtracted:false}));
  }).catch(error=>{console.error(error.message);process.exitCode=1;});
}
