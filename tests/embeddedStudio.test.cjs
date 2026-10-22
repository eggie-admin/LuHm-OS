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
  // Four scenery planes + one interactive glass layer, all scroll vertically.
  assert.deepEqual(studio.depthOffsets(1000),{rear:"-100px",middle:"-220px",front:"-380px"});
  assert.deepEqual(studio.depthOffsets(1000,true),{rear:"0px",middle:"0px",front:"0px"});
  assert.deepEqual(studio.depthOffsets(-100),{rear:"0px",middle:"0px",front:"0px"});
  assert.equal(studio.embedTarget({location:{hostname:"example.invalid",origin:"https://example.invalid"}}),
    "https://luhm-os-godot-harness-green.onrender.com/harness/godot-export/index.html");
  assert.equal(contract.visualDepthStack.decorativePlanes,4);
  assert.deepEqual(contract.visualDepthStack.orderedCompositing.map(row=>row.id),
    ["embeddedBackdrop","rearParallax","middleParallax","glassGui","frontParallax"]);

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
      assert.equal(await page.locator("#lum2dStage").count(),1);
      await page.locator("#lum2dSmile").click();
      assert.equal(await page.locator("#lum2dStage").getAttribute("data-mood"),"neutral");
      await page.locator("#lum2dPause").click();
      assert.equal(await page.locator("#lum2dPause").getAttribute("aria-pressed"),"true");

      assert.equal(await page.locator(".scenery > div").count(),4);
      assert.equal(await page.locator("#studioBackdropFrame").isHidden(),true,"Background iframe must be lazy and inert");
      assert.equal(await page.locator("#studioBackdropFrame").getAttribute("src"),null,"No remote scene before user action");
      assert.equal(await page.evaluate(()=>typeof jQuery.fn.luhmStudioParallax),"function","Standalone jQuery plugin wired");
      assert.equal(await page.locator('[data-studio-depth="frontParallax"]').evaluate(el=>getComputedStyle(el).pointerEvents),"none");
      assert.equal(await page.locator('[data-studio-depth="embeddedBackdrop"]').evaluate(el=>getComputedStyle(el).position),"fixed");

      assert.equal(await page.locator("#studioMusicStage iframe").count(),0);
      assert.equal(external.length,0,"No external player request before click");
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),"No horizontal overflow at "+width);

      await page.evaluate(()=>scrollTo(0,450));
      await page.waitForTimeout(75);
      assert.equal(await page.locator("#luhmStudioDeck").evaluate(el=>el.style.getPropertyValue("--studioRearY")),"0px","Reduced motion has no parallax");
      await page.locator("#studioBackdropLoad").click();
      assert.equal(await page.locator("#studioBackdropFrame").isHidden(),false);
      assert.match(await page.locator("#studioBackdropFrame").getAttribute("src"),/\/harness\/godot-export\/index\.html$/);
      await page.locator("#studioBackdropStop").click();
      assert.equal(await page.locator("#studioBackdropFrame").isHidden(),true);
      assert.equal(await page.locator("#studioBackdropFrame").getAttribute("src"),null);
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
    await page.evaluate(()=>scrollTo(0,400));
    await page.waitForFunction(()=>document.getElementById("luhmStudioDeck").style.getPropertyValue("--studioMiddleY")==="-88px");
    assert.equal(await page.locator('#studioBackdropFrame').getAttribute('src'),null,"ChatGPT frame must not fetch scene automatically");
    assert.equal(await page.locator("#luhmStudioDeck").count(),1);
      assert.equal(await page.locator("[data-stage-plane]").count(),7);
      assert.equal(await page.locator("#lum2dStage").count(),1);
      await page.locator("#lum2dSmile").click();
      assert.equal(await page.locator("#lum2dStage").getAttribute("data-mood"),"neutral");
      await page.locator("#lum2dPause").click();
      assert.equal(await page.locator("#lum2dPause").getAttribute("aria-pressed"),"true");
    assert.deepEqual(errors,[],"MCP widget must start without undefined initializer");
    assert.equal(await page.locator("#studioUndo").isDisabled(),true);
    console.log("PASS MCP widget startup and shared controls");await page.close();
  } finally { await browser.close(); }
}
main().catch(e=>{console.error(e);process.exitCode=1;});
