/* Offline browser regression for the real shared studio and MCP widget. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {webcrypto} = require("node:crypto");
const {chromium} = require("playwright");
const studio = require("../host/harness/studioDeck.js");
const root = path.resolve(__dirname, "..");
const file = name => fs.readFileSync(path.join(root, "host/harness", name), "utf8");
const contract = {...JSON.parse(fs.readFileSync(path.join(root, "doctrine/embeddedStudioV1.json"))),sourceRef:"a".repeat(40),quarantine:{state:"QUARANTINED",activeTaskWorkersAllowed:false}};

async function main() {
  for (const value of ["javascript:alert(1)","http://youtube.com/watch?v=M7lc1UVf-VE","https://youtube.com.evil.example/watch?v=M7lc1UVf-VE","https://youtube.com@evil.example/watch?v=M7lc1UVf-VE","https://youtube.com:444/watch?v=M7lc1UVf-VE","https://youtube.com/watch?v=bad"])
    assert.throws(() => studio.musicTarget(value),value);
  const target = studio.musicTarget("https://music.youtube.com/watch?v=M7lc1UVf-VE&si=tracking");
  assert.equal(target.embed,"https://www.youtube-nocookie.com/embed/M7lc1UVf-VE?autoplay=0&playsinline=1");
  assert.match(studio.musicTarget("https://www.youtube.com/playlist?list=PL1234567890").embed,/videoseries/);
  assert.equal(studio.category("sisters.rar"),"archivesPendingInspection");
  assert.equal(studio.category("scene.GLB"),"models");
  assert.deepEqual(studio.depthOffsets(1000),{far:"-60.0px",near:"-140.0px",front:"-260.0px"});
  assert.deepEqual(studio.depthOffsets(1000,true),{far:"0.0px",near:"0.0px",front:"0.0px"});
  assert.deepEqual(studio.depthOffsets(Infinity),{far:"0.0px",near:"0.0px",front:"0.0px"});
  assert.equal(studio.validContract(contract),true);
  assert.equal(studio.validContract({...contract,lane:"production"}),false);
  assert.equal(studio.validContract({...contract,quarantine:{activeTaskWorkersAllowed:true}}),false);
  const bytes = new TextEncoder().encode("abc");
  assert.equal(await studio.fingerprint({size:3,arrayBuffer:async()=>bytes.buffer},webcrypto),"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
  assert.equal(await studio.fingerprint({size:studio.hashLimit+1,arrayBuffer:()=>{throw Error("must not allocate");}},webcrypto),null);

  const browser = await chromium.launch({headless:true,executablePath:process.env.LUHM_TEST_BROWSER,args:["--no-sandbox"]});
  try {
    for (const width of [320,390,960]) {
      const page = await browser.newPage({viewport:{width,height:900},reducedMotion:"reduce"});
      page.setDefaultTimeout(10000);
      const errors=[];page.on("pageerror",error=>errors.push(error.message));
      const external=[];
      await page.route("https://**",route=>{external.push(route.request().url());return route.abort();});
      await page.goto("http://localhost:8788/harness/");
      await page.locator("#agentLoadingScreen").waitFor({state:"hidden"});
      assert.equal(await page.locator("#luhmStudioDeck").count(),1);
    assert.equal(await page.locator("[data-stage-plane]").count(),7);
    await page.locator("#studioStageExpression").click();
    assert.equal(await page.locator("#studioStageExpression").getAttribute("aria-pressed"),"true");
      assert.equal(await page.locator(".scenery > div").count(),4);
      assert.deepEqual(await page.locator("[data-seven-layer-stage] [data-stage-plane]").evaluateAll(nodes=>nodes.map(n=>n.dataset.stagePlane)),
        ["embeddedMedia","farField","sharpBackground","foregroundAtmosphere","liveCharacter","vectorEffects","glassWidgetDock"]);
      assert.equal(await page.locator("#studioStageBlink").isVisible(),true);
      await page.locator("#studioStageExpression").click();
      assert.equal(await page.locator("#studioStageExpression").getAttribute("aria-pressed"),"true");
      await page.locator("#studioStageBlink").click();
      assert.equal(await page.locator("#studioCharacter").evaluate(el=>el.classList.contains("is-blinking")),true);
      await page.locator("#studioStageMotion").click();
      assert.equal(await page.locator("#studioStageMotion").getAttribute("aria-pressed"),"true");
      assert.equal(await page.locator("#studioSevenLayerStage").evaluate(el=>el.style.getPropertyValue("--stage-front")),"0.0px");
      assert.equal(await page.locator("#studioMusicStage iframe").count(),0);
      assert.equal(external.length,0,"No external player request before click");
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),"No horizontal overflow at "+width);
      await page.locator("#studioMusicUrl").fill("https://evil.example/x");
      await page.locator("#studioMusicLoad").click();
      assert.equal(await page.locator("#studioMusicStage iframe").count(),0);
      await page.locator("#studioMusicUrl").fill("https://music.youtube.com/watch?v=M7lc1UVf-VE");
      await page.locator("#studioMusicLoad").click();
      assert.match(await page.locator("#studioMusicStage iframe").getAttribute("src"),/^https:\/\/www.youtube-nocookie.com\/embed\//);
      const box=await page.locator("#studioMusicStage iframe").boundingBox();
      assert.ok(box.width>=200&&box.height>=200,"Visible player minimum");
      assert.equal(await page.locator("#studioMusicStage iframe").getAttribute("referrerpolicy"),"strict-origin-when-cross-origin");
      await page.locator("#studioMusicStop").click();
      assert.equal(await page.locator("#studioMusicStage iframe").count(),0);
      await page.locator("#studioAssetInput").setInputFiles([
        {name:"one.glb",mimeType:"model/gltf-binary",buffer:Buffer.from("abc")},
        {name:"duplicate.glb",mimeType:"model/gltf-binary",buffer:Buffer.from("abc")},
        {name:"unknown.rar",mimeType:"application/octet-stream",buffer:Buffer.from("archive fixture")}
      ]);
      await page.getByText(/2 assets · 2 fingerprinted/).waitFor();
      const records=await page.evaluate(()=>window.luhmStudioDeck.register());
      assert.equal(records.length,2);assert.ok(records.every(x=>x.rights==="UNKNOWN"&&x.canon==="UNAPPROVED"));
      assert.equal(records[1].category,"archivesPendingInspection");
      const downloadPromise=page.waitForEvent("download");await page.locator("#studioAssetExport").click();
      const download=await downloadPromise;const exported=JSON.parse(fs.readFileSync(await download.path(),"utf8"));
      assert.equal(exported.productionPromotion,false);assert.equal(exported.assets.length,2);
      const schemaFile=process.env.LUHM_STUDIO_EXPORT;
      if(schemaFile)fs.writeFileSync(schemaFile,JSON.stringify(exported));
      assert.deepEqual(errors,[],"No startup JavaScript errors");
      console.log("PASS studio interaction and mobile layout "+width);await page.close();
    }
    const page=await browser.newPage();const errors=[];page.on("pageerror",e=>errors.push(e.message));
    let widget=file("widget.html");
    widget=widget.replace("<!-- LUHM_STUDIO_DECK -->","<style>"+file("studioDeck.css")+"</style>"+file("studioDeck.html")+"<script>"+file("studioDeck.js")+"</script>");
    await page.setContent(widget);
    assert.equal(await page.locator("#studioStatus").textContent(),"VERIFY · studio source contract pending");
    assert.equal(await page.locator("#luhmStudioDeck").count(),1);
    assert.deepEqual(errors,[],"MCP widget must start without undefined initializer");
    assert.equal(await page.locator("#studioUndo").isDisabled(),true);
    console.log("PASS MCP widget startup and shared controls");await page.close();
  } finally { await browser.close(); }
}
main().catch(e=>{console.error(e);process.exitCode=1;});
