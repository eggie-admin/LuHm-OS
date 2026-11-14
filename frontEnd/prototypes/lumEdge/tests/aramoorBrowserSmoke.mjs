/* Exact-source browser proof. Only runs in isolated CI; never installs or publishes remote runtime. */
import {chromium} from "playwright";
import {mkdir,readFile,writeFile} from "node:fs/promises";
import {createHash} from "node:crypto";
import assert from "node:assert/strict";
const output=new URL("../build/aramoor-browser/",import.meta.url);
await mkdir(output,{recursive:true});
let browser;
try {
  browser=await chromium.launch({
    headless:true,
    args:["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--disable-dev-shm-usage","--no-sandbox"]
  });
  const context=await browser.newContext({viewport:{width:1440,height:900},deviceScaleFactor:1});
  const page=await context.newPage();
  const pageErrors=[];
  page.on("pageerror",e=>pageErrors.push(String(e.message||e)));
  await page.goto("http://127.0.0.1:4174/aramoor.html",{waitUntil:"domcontentloaded",timeout:25000});
  await page.waitForFunction(()=>globalThis.__aramoorProof?.ready===true,{timeout:30000});
  await page.waitForFunction(()=>globalThis.__aramoorProof?.metrics()?.frames>8,{timeout:15000});
  const baseline=await page.evaluate(()=>globalThis.__aramoorProof.metrics());
  assert.equal(baseline.zoneCount,9);
  assert.equal(baseline.bridgeCount,12);
  assert.ok(baseline.meshCount>120,"Procedural 3D geometry must be in the browser");
  assert.ok(baseline.webGlVersion>=1,"Real WebGL context required");
  assert.equal(baseline.normalTexturePresent,true,"Procedural PBR normal map must be mounted");
  assert.equal(baseline.tide,"livingTide");
  assert.equal(pageErrors.length,0,"No JavaScript exceptions allowed: "+pageErrors.join("; "));
  await page.screenshot({path:new URL("aramoor-living-tide.png",output).pathname,animations:"disabled"});
  await page.locator('#region-list button[data-region="saltglassBoardwalk"]').click();
  assert.equal(await page.locator('#region-list button[data-region="saltglassBoardwalk"]').getAttribute("aria-current"),"location");
  await page.getByTestId("tide-toggle").click();
  const ghost=await page.evaluate(()=>globalThis.__aramoorProof.metrics());
  assert.equal(ghost.tide,"ghostTide");
  assert.ok(ghost.meshCount>120);
  await page.screenshot({path:new URL("aramoor-ghost-tide.png",output).pathname,animations:"disabled"});
  await page.getByTestId("world-reset").click();
  assert.equal(await page.locator('#region-list button[data-region="aramoorHarbor"]').getAttribute("aria-current"),"location");
  const results={schema:"luhmOs.aramoorBrowserProof.v1",status:"CHROMIUM_WEBGL_SOURCE_PROOF",
    baseline,ghost,travel:"PASS",tideSwitch:"PASS",reset:"PASS",pageErrors,
    sourceSha:process.env.GITHUB_SHA||"local",crown:"STOP",browserOnly:true,
    publicDeployment:false,engineAuthority:"Godot remains separate"};
  for(const name of ["aramoor-living-tide.png","aramoor-ghost-tide.png"]){
    const bytes=await readFile(new URL(name,output));
    assert.ok(bytes.length>30000,name+" is unexpectedly small");
    results[name]={bytes:bytes.length,sha256:createHash("sha256").update(bytes).digest("hex")};
  }
  assert.notEqual(results["aramoor-living-tide.png"].sha256,results["aramoor-ghost-tide.png"].sha256,
    "Tide screenshots must differ");
  await writeFile(new URL("browser-proof.json",output),JSON.stringify(results,null,2)+"\n");
  console.log("ARAMOOR_CHROMIUM_VISUAL_PROOF_GREEN");
  console.log(JSON.stringify(results,null,2));
  await context.close();
} finally {
  await browser?.close();
}
