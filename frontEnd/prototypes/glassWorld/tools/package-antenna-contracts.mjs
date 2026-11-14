import {mkdirSync,copyFileSync,writeFileSync} from "node:fs";
import {execFileSync} from "node:child_process";
const directory="dist/antenna-contracts";
mkdirSync(directory,{recursive:true});
for(const file of ["antenna-policy.mjs","animation-contract.mjs","widget-bridge.mjs"])copyFileSync("src/"+file,directory+"/"+file);
writeFileSync(directory+"/package.json",JSON.stringify({name:"@luhm/antenna-contracts",version:"0.1.0",private:true,type:"module",
  description:"Dependency-free LuHm antenna, animation and MCP widget contracts",
  exports:{"./antenna":"./antenna-policy.mjs","./animation":"./animation-contract.mjs","./widgetBridge":"./widget-bridge.mjs"},
  files:["*.mjs"]},null,2));
execFileSync("npm",["pack","./"+directory,"--pack-destination","dist","--ignore-scripts"],{stdio:"inherit"});
