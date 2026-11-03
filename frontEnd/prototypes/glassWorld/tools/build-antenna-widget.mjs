import {build} from "vite";
import {readFileSync,writeFileSync,mkdirSync,readdirSync,statSync} from "node:fs";
import {createHash} from "node:crypto";
import {antennaBudget} from "../src/animation-contract.mjs";
const result=await build({configFile:false,logLevel:"warn",build:{write:false,minify:true,
  lib:{entry:"src/antenna-widget.js",name:"LuHmAntenna",formats:["iife"]}}});
const outputs=(Array.isArray(result)?result:[result]).flatMap(item=>item.output);
const scripts=outputs.filter(item=>item.type==="chunk");
if(scripts.length!==1||scripts[0].imports.length||scripts[0].dynamicImports.length)throw Error("Widget must be one self-contained script");
const css=outputs.filter(item=>item.type==="asset"&&item.fileName.endsWith(".css")).map(item=>item.source).join("\n");
const vueLicense=readFileSync("node_modules/vue/LICENSE","utf8");
const escapeScript=text=>text.replace(/<\/script/gi,"<\\/script");
const page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LuHm animation antenna</title><style>'+css.replace(/<\/style/gi,"<\\/style")+'</style></head><body><main id="antenna"></main><script>/* Vue license\n'+vueLicense.replace(/\*\//g,"* /")+'*/\n'+escapeScript(scripts[0].code)+'</script></body></html>';
const bytes=Buffer.byteLength(page);
if(bytes>antennaBudget.widgetBytes)throw Error("Widget budget exceeded: "+bytes);
mkdirSync("dist",{recursive:true});writeFileSync("dist/antennaWidget.html",page);
function size(directory){return readdirSync(directory,{withFileTypes:true}).reduce((sum,item)=>sum+(item.isDirectory()?size(directory+"/"+item.name):statSync(directory+"/"+item.name).size),0);}
const totalDistBytes=size("dist");
if(totalDistBytes>antennaBudget.totalBytes)throw Error("Total antenna/studio package budget exceeded");
writeFileSync("dist/antennaWidget.receipt.json",JSON.stringify({schema:"luhmOs.widgetBuild.v1",bytes,totalDistBytes,
  totalExcludesReceipt:true,sha256:createHash("sha256").update(page).digest("hex"),budget:antennaBudget,externalAssets:0,modelsBundled:0},null,2));
console.log("ANTENNA_WIDGET_BUILD "+bytes+" bytes; zero external assets");
