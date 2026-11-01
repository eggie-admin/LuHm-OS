import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const file=p=>readFileSync(new URL("../"+p,import.meta.url),"utf8");
const vault=JSON.parse(file("doctrine/goddessGlassVaultReconciliationV1.json"));
const canon=JSON.parse(file("game/canon/CHARACTER_CANON_V1.json"));
const ingest=JSON.parse(file("game/assets/CHARACTER_ASSET_INGEST_V1.json"));
test("Drive asset candidate follows existing four-character identity canon",()=>{
  assert.equal(vault.schema,"luhmOs.goddessGlassVaultReconciliation.v1");
  assert.equal(vault.status,"PRIVATE_VAULT_INDEXED_LIVE_PLUGIN_NOT_UPDATED");
  assert.deepEqual(vault.roster.slice(0,4).map(x=>x.id),["lum","urd","belldandy","skuld"]);
  for(const x of vault.roster.slice(0,4)){
    assert.ok(canon.characters[x.id]);assert.ok(ingest.characters[x.id]);
    assert.equal(x.liveRigStatus==="UNPROVEN"||x.liveRigStatus==="NOT_FOUND",true);
  }
  assert.equal(vault.roster[4].baseline,"ART_STUDIO_ROLE_PREVIEW_ONLY");
});
test("verified Drive media bytes and sky plate metadata are not mislabeled 3D",()=>{
  assert.equal(vault.availableVault.lumAnimatedVideo.sha256,
    "1a20bd7bf495ee930d2cc9dab9342d7cb29d326ce0c7f433c206581ebdddad97");
  assert.equal(vault.availableVault.lumAnimatedVideo.threeDimensionalModel,false);
  assert.equal(vault.availableVault.lumHistoricGlbPack.liveGodotImportProven,false);
  assert.equal(vault.availableVault.skyPlates.length,3);
  for(const x of vault.availableVault.skyPlates){
    assert.equal(x.role,"2D_PARALLAX_SKY_NOT_HDRI");
    assert.match(x.sha256,/^[0-9a-f]{64}$/);
  }
  assert.equal(vault.runtime.realGlbRuntimeLoaded,false);
  assert.equal(vault.runtime.actualCubemapHdrSkybox,false);
});
test("public GitHub metadata contains no private binary/Drive IDs or false plugin promotion",()=>{
  assert.equal(vault.noRawPrivateDriveIdsInPublicGit,true);
  assert.equal(vault.noPrivateBinaryAssetsInPublicGit,true);
  assert.equal(vault.runtime.glassDockNewVersionMounted,false);
  assert.equal(vault.runtime.pluginReadOnlyMobileCockpitInvoked,true);
  assert.equal(vault.runtime.newerDraftSourceNeedsDeployment,true);
  assert.equal(vault.runtime.cloudflareRemoteRequired,false);
  assert.equal(vault.gates.publicReleaseAuthorized,false);
  assert.equal(vault.crownStatus,"STOP");
  const raw=file("doctrine/goddessGlassVaultReconciliationV1.json");
  assert.doesNotMatch(raw,/drive\.google\.com\/file\/d\//);
  assert.doesNotMatch(raw,/data:video\/mp4;base64,/);
  assert.doesNotMatch(raw,/KAI9000_LUM_AVATAR_ACTUAL_ANIMATED\.mp4"\s*:\s*"data:/);
});