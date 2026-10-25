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
      // The first-screen mobile app must display real, routed features instead of an audit wall.
      assert.equal(await page.locator("#crownStart").isVisible(),true,"Professor launch deck visible");
      assert.equal(await page.locator("#crownStart [data-crown-plane]").count(),7,"Seven CSS planes in first-screen launch");
      assert.equal(await page.locator("#crownStart .crownQuickActions button").count(),5,"Five obvious touch actions");
      assert.equal(await page.locator("#crownViewportSlot .godot #godotFrame").count(),1,"The ONE real Godot viewport is in the first screen");
      assert.equal(await page.locator("#godotFrame").getAttribute("src"),null,"No remote 3D requests on arrival");
      assert.equal(await page.locator("#playFirstNight").isEnabled(),true,"Play action no longer incorrectly disabled");
      await page.locator("#crownLaunchLum").click();
      assert.equal(await page.locator("#studioPrivateLumFile").evaluate(el=>document.activeElement===el),true,"Private Lum picker is one tap away");
      await page.locator("#crownLaunchMusic").click();
      assert.equal(await page.locator("#studioMusicUrl").evaluate(el=>document.activeElement===el),true,"Music plugin is one tap away");
      await page.locator("#crownLaunchGlass").click();
      assert.equal(await page.locator("#studioGlassDock").isVisible(),true,"Actual glass dock from launch");
      await page.locator("#crownLaunchLayers").click();
      assert.equal(await page.locator("#studioPlaneInspector").getAttribute("open"),"","Seven studio layer inspector is opened");
      await page.locator("#studioGlassClose").click();
      assert.equal(external.length,0,"No external fetch until Professor explicitly presses Play");
      await page.locator("#crownLaunchGodot").click();
      assert.equal(await page.locator("#playGodotRemote").getAttribute("aria-pressed"),"true","Primary Play opens the existing Godot host");
      assert.equal(await page.locator("#godotFrame").getAttribute("src"),
        "https://luhm-os-godot-harness-green.onrender.com/harness/godot-export/index.html","Pinned Godot embed");
      assert.match(await page.locator("#crownLaunchStatus").textContent(),/not verified/,"Never claim unproven gameplay");
      assert.ok(external.every(url=>url.startsWith("https://luhm-os-godot-harness-green.onrender.com/")),"Only the pinned service may be requested");
      await page.locator("#playGodotRemote").click();
      assert.equal(await page.locator("#godotFrame").getAttribute("src"),null,"Player closes without a leftover iframe source");
      external.length=0; // From here, test that local private artwork and music remain no-network until consent.

      assert.equal(await page.locator("[data-stage-plane]").count(),7);
      await page.locator("#pocketbond").click();
      assert.match(await page.locator("#pocketexpression").textContent(),/Bond level 1/);
      await page.locator("#pocketpalette").selectOption("pink");
      assert.equal(await page.locator("#pocketpetBody").getAttribute("fill"),"#e95cb5");
      assert.equal(await page.locator("#lum2dStage").count(),1);
      await page.locator("#lum2dSmile").click();
      assert.equal(await page.locator("#lum2dStage").getAttribute("data-mood"),"neutral");
      await page.locator("#lum2dPause").click();
      assert.equal(await page.locator("#lum2dPause").getAttribute("aria-pressed"),"true");

      // No original art in public CI: a tiny generated GIF exercises private local selection.
      const proofPicker=page.locator("#studioPrivateLumFile");
      assert.equal(await page.locator("#studioPrivateLumStage").isHidden(),true,"No background asset loading");
      await proofPicker.setInputFiles({name:"synthetic.gif",mimeType:"image/gif",
        buffer:Buffer.from("R0lGODdhAgACAIEAAP8A/wAAAAAAAAAAACwAAAAAAgACAAAIBgABCAQQEAA7","base64")});
      await page.getByText(/DIFFERENT LOCAL CANDIDATE/).waitFor();
      assert.equal(await page.locator("#studioPrivateLumStage").isVisible(),true,"Synthetic GIF decoded locally");
      assert.equal(await page.locator("#studioPrivateLumImage").evaluate(el=>el.naturalWidth),2);
      assert.equal(await page.locator("#studioPrivateLumPause").getAttribute("aria-pressed"),"true","Reduced motion is static");
      await page.locator("#studioPrivateLumPause").click();
      assert.equal(await page.locator("#studioPrivateLumPause").getAttribute("aria-pressed"),"false","Playback requires tap");
      await page.locator("#studioPrivateLumPause").click();
      assert.equal(await page.locator("#studioPrivateLumPause").getAttribute("aria-pressed"),"true","Pause restores still");
      await page.locator("#studioPrivateLumClear").click();
      assert.equal(await page.locator("#studioPrivateLumStage").isHidden(),true,"Clear revokes local preview");
      await proofPicker.setInputFiles({name:"fake.gif",mimeType:"image/gif",buffer:Buffer.from("not-a-real-gif")});
      await page.getByText(/GIF inspection failed/).waitFor();
      assert.equal(await page.locator("#studioPrivateLumStage").isHidden(),true,"Reject spoofed GIF");
      assert.equal(external.length,0,"No remote requests from private art picker");
      assert.equal(await page.locator(".scenery > div").count(),4);
      assert.equal(await page.locator("#studioBackdropFrame").isHidden(),true,"Background iframe must be lazy and inert");
      assert.equal(await page.locator("#studioBackdropFrame").getAttribute("src"),null,"No remote scene before user action");
      assert.equal(await page.evaluate(()=>typeof jQuery.fn.luhmStudioParallax),"function","Standalone jQuery plugin wired");
      assert.equal(await page.evaluate(()=>typeof jQuery.fn.luhmMusicDeck),"function","Real jQuery music plugin wired");
      const launcher=page.locator("#studioGlassToggle");
      await launcher.click();
      assert.equal(await launcher.getAttribute("aria-expanded"),"true","Glass launcher opens");
      assert.equal(await page.locator("#studioGlassDock").isVisible(),true,"Real glass panel appears");
      assert.equal(await page.locator("#studioGlassDock [data-studio-route]").count(),5,"Five glass modules");
      assert.equal(await page.locator("#studioGlassClose").evaluate(el=>document.activeElement===el),true,"Dock takes focus");
      await page.locator('[data-studio-route="music"]').click();
      assert.equal(await page.locator("#studioGlassDock").isHidden(),true,"Music route closes flyout");
      assert.equal(await page.locator("#studioMusicUrl").evaluate(el=>document.activeElement===el),true,"Music module focuses real player");
      await launcher.click();
      await page.locator('[data-studio-route="avatars"]').click();
      assert.equal(await page.locator("#lum2dStage").evaluate(el=>document.activeElement===el),true,"Avatar module focuses real controls");
      await launcher.click();
      await page.locator('[data-studio-route="yume"]').click();
      assert.equal(await page.locator("#studioAssetInput").evaluate(el=>document.activeElement===el),true,"Yume module focuses asset desk");
      await launcher.click();
      await page.locator('[data-studio-route="social"]').click();
      assert.match(await page.locator("#studioGlassStatus").textContent(),/No posting tool is connected/,"No invented publication service");
      await page.locator('[data-studio-route="admin"]').click();
      assert.equal(await page.locator("#studioPlaneInspector").getAttribute("open"),"","Admin opens layer inspector");
      assert.equal(await page.locator("#studioPlaneInspector li").count(),7,"Seven explicitly visible plane descriptions");
      await page.keyboard.press("Escape");
      assert.equal(await page.locator("#studioGlassDock").isHidden(),true,"Escape closes glass dock");
      assert.equal(await launcher.evaluate(el=>document.activeElement===el),true,"Glass focus returns");
      assert.equal(await page.locator('[data-studio-depth="frontParallax"]').evaluate(el=>getComputedStyle(el).pointerEvents),"none");
      assert.equal(await page.locator('[data-studio-depth="embeddedBackdrop"]').evaluate(el=>getComputedStyle(el).position),"fixed");

      assert.equal(await page.locator("#studioMusicStage iframe").count(),0);
      assert.equal(external.length,0,"No external player request before click");
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),"No horizontal overflow at "+width);

      await page.evaluate(()=>scrollTo(0,450));
      await page.waitForTimeout(75);
      assert.equal(await page.locator("#luhmStudioDeck").evaluate(el=>el.style.getPropertyValue("--studioRearY")),"0px","Reduced motion has no parallax");
      await page.locator("#playGodotRemote").click();
      assert.equal(await page.locator("#playGodotRemote").getAttribute("aria-pressed"),"true","Remote embed requires click");
      assert.equal(await page.locator("#godotFrame").getAttribute("src"),
        "https://luhm-os-godot-harness-green.onrender.com/harness/godot-export/index.html","Only pinned Godot origin");
      assert.match(await page.locator("#playStatus").textContent(),/unverified/,"No fake Godot runtime green");
      await page.locator("#playGodotRemote").click();
      assert.equal(await page.locator("#godotFrame").getAttribute("src"),null,"Godot disconnect clears network frame");
      await page.locator("#studioBackdropLoad").click();
      assert.equal(await page.locator("#studioBackdropFrame").isHidden(),false);
      assert.match(await page.locator("#studioBackdropFrame").getAttribute("src"),/\/harness\/godot-export\/index\.html$/);
      await page.locator("#studioBackdropStop").click();
      assert.equal(await page.locator("#studioBackdropFrame").isHidden(),true);
      assert.equal(await page.locator("#studioBackdropFrame").getAttribute("src"),null);
      await page.locator("#studioMusicUrl").fill("");
      await page.locator("#studioMusicLoad").click();
      assert.match(await page.locator("#studioMusicStatus").textContent(),/Paste a YouTube video or playlist link first/,"Blank music input is friendly");
      assert.equal(await page.locator("#studioMusicStage iframe").count(),0,"No network on blank music input");
      await page.locator("#studioMusicUrl").fill("https://evil.example/x");
      await page.locator("#studioMusicLoad").click();
      assert.equal(await page.locator("#studioMusicStage iframe").count(),0);
      await page.locator("#studioMusicUrl").fill("https://music.youtube.com/watch?v=M7lc1UVf-VE");
      await page.locator("#studioMusicLoad").click();
      assert.match(await page.locator("#studioMusicStage iframe").getAttribute("src"),/^https:\/\/www.youtube-nocookie.com\/embed\//);
      assert.equal(await page.locator("#retroMusicShell").getAttribute("class"),"retroMusicShell is-loaded","Retro music skin responds to connect");
      const box=await page.locator("#studioMusicStage iframe").boundingBox();
      assert.ok(box.width>=200&&box.height>=200,"Visible player minimum");
      assert.equal(await page.locator("#studioMusicStage iframe").getAttribute("referrerpolicy"),"strict-origin-when-cross-origin");
      await page.locator("#studioMusicStop").click();
      assert.equal(await page.locator("#studioMusicStage iframe").count(),0);
      assert.equal(await page.locator("#retroMusicShell").getAttribute("class"),"retroMusicShell","Retro music skin resets on eject");
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
      await page.locator("#pocketbond").click();
      assert.match(await page.locator("#pocketexpression").textContent(),/Bond level 1/);
      await page.locator("#pocketpalette").selectOption("pink");
      assert.equal(await page.locator("#pocketpetBody").getAttribute("fill"),"#e95cb5");
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
