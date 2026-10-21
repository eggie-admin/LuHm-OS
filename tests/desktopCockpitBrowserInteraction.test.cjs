"use strict";
/* Browser interaction proof against the real local Python3 MCP server.
 * No private donor assets, external player network, or ChatGPT-host claims.
 */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {chromium}=require("playwright");
const HOST="http://localhost:8788/harness/";
const OUT=path.resolve("build/desktop-browser-proof");

const validPng=Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO/oVlkAAAAASUVORK5CYII=","base64");
const file=(name,mimeType,buffer)=>({name,mimeType,buffer});
const apiErrors=[];

async function inspect(browser,width){
 const page=await browser.newPage({viewport:{width,height:850},reducedMotion:"reduce",acceptDownloads:true});
 page.setDefaultTimeout(20000);
 const errors=[],unexpectedHttps=[],unsafeWrites=[];
 page.on("pageerror",e=>errors.push(String(e.message).slice(0,200)));
 page.on("request",req=>{
   if(req.url().startsWith("https://")) unexpectedHttps.push(req.url());
   if(!["GET","HEAD"].includes(req.method())) unsafeWrites.push(req.method()+" "+req.url());
 });
 await page.route("https://**",route=>route.abort());
 await page.goto(HOST,{waitUntil:"domcontentloaded"});
 await page.locator("#agentLoadingScreen").waitFor({state:"hidden",timeout:20000});
 const crew=page.locator("[data-luhm-cast]");
 assert.equal(await crew.count(),6,"Lum, 4 art goddesses and the human Professor must be visible");
 for (const id of ["lum","urd","belldandy","skuld","yume","human"]) {
   assert.equal(await page.locator('[data-luhm-cast="'+id+'"]').count(),1,"Missing art cabinet member "+id);
 }
 assert.match(await page.locator('[data-luhm-cast="human"]').innerText(),/approval.*REQUIRED/i);
 assert.match(await page.locator("#humanCastPanel").innerText(),/worker routes remain quarantined/i);
 assert.equal(await page.locator("#assetCounter").innerText(),"0 / 0");
 assert.equal(await page.locator("#petName").innerText(),"Lum");
 await page.locator("#petDock").click();
 assert.equal(await page.locator("#petName").innerText(),"Kiri");
 await page.reload({waitUntil:"domcontentloaded"});
 await page.locator("#agentLoadingScreen").waitFor({state:"hidden",timeout:20000});
 assert.equal(await page.locator("#petName").innerText(),"Kiri","pet selection must survive same-tab reload");
 assert.equal(await page.locator("#lum2dStage").count(),1,"Original 2D puppet should mount");
 assert.match(await page.locator("#lum2dMessage").innerText(),/Lum is ready/);
 await page.locator("#lum2dBlink").click();
 assert.match(await page.locator("#lum2dMessage").innerText(),/blinked/i);
 await page.locator("#lum2dSmile").click();
 assert.equal(await page.locator("#lum2dSmile").getAttribute("aria-pressed"),"false");
 assert.equal(await page.locator("#lum2dStage").getAttribute("data-mood"),"neutral");
 await page.locator("#lum2dWave").click();
 assert.match(await page.locator("#lum2dMessage").innerText(),/Motion is reduced/);
 await page.locator("#lum2dPause").click();
 assert.equal(await page.locator("#lum2dPause").getAttribute("aria-pressed"),"true");
 assert.equal(await page.locator("#lum2dStage").evaluate(el=>el.style.getPropertyValue("--l2x")),"0px");
 await page.locator("#lum2dPause").click();
 assert.equal(await page.locator("#lum2dPause").getAttribute("aria-pressed"),"false");

 await page.locator('[data-luhm-mode="ic"]').click();
 assert.equal(await page.locator('[data-luhm-mode="ic"]').getAttribute("aria-pressed"),"true");
 assert.equal(await page.locator('[data-luhm-mode="default"]').getAttribute("aria-pressed"),"false");

 const intake=page.locator("#assetInput");
 await intake.setInputFiles([
   file("green.png","image/png",validPng),
   file("disallowed.svg","image/svg+xml",Buffer.from("<svg/>")),
   file("not-a-png.png","text/html",Buffer.from("<script>1</script>")),
   file("privateName<img>.jpg","image/jpeg",Buffer.from("bytes-not-rendered"))
 ]);
 await page.getByText(/2 added, 2 skipped/).waitFor();
 assert.equal(await page.locator("#assetCounter").innerText(),"1 / 2");
 assert.equal(await page.locator("#thumbRail .thumb").count(),2);
 assert.equal(await page.locator("#assetTree img").count(),0,"filename must not inject HTML");
 assert.equal(await page.locator("#assetTree script").count(),0);
 assert.equal(await page.locator("#pdfPreview").getAttribute("sandbox"),"");
 await page.locator("#nextAsset").click();
 assert.equal(await page.locator("#assetCounter").innerText(),"2 / 2");
 await page.locator("#prevAsset").click();
 assert.equal(await page.locator("#assetCounter").innerText(),"1 / 2");

 const stats=await page.evaluate(()=>({
   width:innerWidth,
   scroll:document.documentElement.scrollWidth,
   reduced:matchMedia("(prefers-reduced-motion: reduce)").matches,
   focusOutline:getComputedStyle(document.querySelector("#petDock")).outlineStyle,
   bg:getComputedStyle(document.querySelector("body")).backgroundColor,
   offlineStatus:document.getElementById("edgeBadge").textContent
 }));
 assert.ok(stats.scroll<=stats.width+1,"horizontal overflow: "+JSON.stringify(stats));
 assert.ok(stats.reduced,"reduced motion not honored");
 await page.locator("#clearAssets").click();
 assert.equal(await page.locator("#assetCounter").innerText(),"0 / 0");
 assert.match(await page.locator("#deskStatus").innerText(),/preview URLs revoked/);
 assert.equal(await page.locator("#assetTree .treeItem").count(),1,"stale media records after Clear");
 assert.equal(await page.locator("#imagePreview").getAttribute("src"),null);
 assert.deepEqual(unexpectedHttps,[],"unexpected cross-origin request");
 assert.deepEqual(unsafeWrites,[],"browser uploads must not happen");
 assert.deepEqual(errors,[],"uncaught JavaScript exceptions");
 fs.mkdirSync(OUT,{recursive:true});
 await page.screenshot({path:path.join(OUT,"desktop-"+width+".png"),fullPage:true});
 await page.close();
 return {width,viewportNoOverflow:true,petControl:true,modeControl:true,
  localPreview:true,spoofedInputsRejected:true,clearRevokesUrls:true,
  pageErrors:errors,networkWrites:unsafeWrites};
}

async function inspectOffline(browser){
 const page=await browser.newPage({viewport:{width:1366,height:820},reducedMotion:"reduce"});
 page.setDefaultTimeout(18000);
 await page.route("**/harness/config.json",route=>route.fulfill({
   status:503,contentType:"application/json",body:JSON.stringify({error:"controlled offline test"})
 }));
 await page.goto(HOST,{waitUntil:"domcontentloaded"});
 await page.locator("#agentLoadingScreen").waitFor({state:"hidden",timeout:18000});
 assert.equal(await page.locator("#petName").innerText(),"Lum","offline fallback companion must remain visible");
 assert.match(await page.locator("#edgeBadge").innerText(),/OFFLINE/);
 await page.locator("#assetInput").setInputFiles([
   file("offline.png","image/png",validPng),
   file("offlineTwo.png","image/png",validPng)
 ]);
 await page.getByText(/2 added, 0 skipped/).waitFor();
 assert.equal(await page.locator("#assetCounter").innerText(),"1 / 2");
 await page.locator("#nextAsset").click();
 assert.equal(await page.locator("#assetCounter").innerText(),"2 / 2");
 await page.locator("#prevAsset").click();
 assert.equal(await page.locator("#assetCounter").innerText(),"1 / 2");
 await page.locator("#clearAssets").click();
 assert.equal(await page.locator("#assetCounter").innerText(),"0 / 0");
 fs.mkdirSync(OUT,{recursive:true});
 await page.screenshot({path:path.join(OUT,"desktop-offline.png"),fullPage:true});
 await page.close();
 return {offlineOverlayDismissed:true,offlineMediaDeskUsable:true};
}

(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try{
   const layouts=[];
   for(const width of [390,1440])layouts.push(await inspect(browser,width));
   const offline=await inspectOffline(browser);
   const result={schema:"luhmOs.desktopBrowserInteraction.v1",
    status:"BROWSER_UI_CONTROLS_PASS",
    sourceRef:process.env.GITHUB_SHA||"LOCAL_HEAD",
    browser:"Playwright Chromium on GitHub Actions Ubuntu",
    layouts,offline,scriptErrors:apiErrors,
    liveRenderInteractionProven:false,
    actualCinnamonDesktopProven:false,
    samsungAppProven:false,
    chatGptInChatMountProven:false,
    crownStatus:"STOP"};
   fs.writeFileSync(path.join(OUT,"receipt.json"),JSON.stringify(result,null,2)+"\n");
   console.log("GREEN_DESKTOP_CHROMIUM_INTERACTION_AND_OFFLINE_RECOVERY");
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
