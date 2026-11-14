"use strict";
(() => {
  const baseUrl = "https://github.com/eggie-admin/LuHm-OS/blob/main/";
  const storageKey = "luhmOs.canonControlRoom.localState.v1";
  const localSchema = "luhmOs.canonControlRoomLocalState.v1";
  const viewIds = ["overview", "systems", "assets", "agents", "compliance", "gaps", "audit", "deploy"];
  const statuses = ["implemented", "tentative", "missing", "blocked"];
  const auditStates = ["notStarted", "inProgress", "completed", "blocked"];
  const byId = (id) => document.getElementById(id);
  const safe = (value) => String(value ?? "").replace(/[&<>"']/g, (m) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]));
  const safePath = (path) => /^[a-zA-Z0-9_./-]+$/.test(path || "") ? baseUrl + path : baseUrl + "README.md";
  const label = (value) => ({implemented:"SOURCE",tentative:"TENTATIVE",missing:"MISSING",blocked:"BLOCKED",sourceConfigured:"SOURCE ROLE",planned:"PLANNED",notAsyncRuntime:"NOT ASYNC"}[value] || String(value).replace(/([A-Z])/g," $1").toUpperCase());
  let model = null;
  let state = {schema:localSchema,checked:{},gaps:{},audits:{},history:[]};
  let activeView = "overview";

  function notice(message) { byId("liveNotice").textContent = message; }
  function cleanState(candidate) {
    const next = {schema:localSchema,checked:{},gaps:{},audits:{},history:[]};
    if (!candidate || candidate.schema !== localSchema) return next;
    for (const c of model.compliance) if (typeof candidate.checked?.[c.id] === "boolean") next.checked[c.id] = candidate.checked[c.id];
    for (const g of model.gaps) {
      const v = candidate.gaps?.[g.id];
      if (v && typeof v === "object") next.gaps[g.id] = {
        status:statuses.includes(v.status) ? v.status : g.status,
        note:typeof v.note === "string" ? v.note.slice(0,2500) : ""
      };
    }
    for (const a of model.auditStages) if (auditStates.includes(candidate.audits?.[a.id]) && !(a.id === "deploy" && candidate.audits[a.id] === "completed")) next.audits[a.id] = candidate.audits[a.id];
    if (Array.isArray(candidate.history)) next.history = candidate.history.slice(-250).filter(x => x && typeof x.event === "string").map(x=>({at:String(x.at||"").slice(0,40),event:String(x.event).slice(0,200)}));
    return next;
  }
  function store(event) {
    state.history.push({at:new Date().toISOString(),event});
    state.history = state.history.slice(-250);
    try { localStorage.setItem(storageKey,JSON.stringify(state)); notice("Browser-only update saved. Export JSON to create a reviewable GitHub proposal."); }
    catch { notice("Browser storage unavailable. Export JSON now to keep these local edits."); }
    renderMetrics();
  }
  function statusBadge(status) { return '<span class="state ' + safe(statuses.includes(status) ? status : "tentative") + '">' + safe(label(status)) + "</span>"; }
  function sourceAnchor(path) { return '<a class="sourceLink" href="' + safe(safePath(path)) + '" target="_blank" rel="noopener noreferrer">' + safe(path) + " ↗</a>"; }

  function renderMetrics() {
    const counts = Object.fromEntries(statuses.map(x => [x,model.systems.filter(s=>s.status===x).length]));
    const details = [
      ["IMPLEMENTED SOURCE",counts.implemented,"Source present ≠ runtime GREEN"],
      ["TENTATIVE",counts.tentative,"Unverified integrations"],
      ["MISSING",counts.missing,"Source gap / no confirmed proof"],
      ["BLOCKED",counts.blocked,"Rights, host or security stop"]
    ];
    byId("metricCards").innerHTML = details.map(d=>'<div class="metric"><div class="metricName">'+safe(d[0])+'</div><strong>'+d[1]+'</strong><small>'+safe(d[2])+'</small></div>').join("");
  }
  function renderOverview() {
    byId("priorityActions").innerHTML = model.priorityActions.map(p=>'<li><strong>'+safe(p.title)+'</strong><small>'+safe(p.detail)+'</small></li>').join("");
    const signals = ["main remains source authority","candidate branch only","private Drive binaries withheld","agent backend quarantined","3D Lum runtime unverified","no hidden async worker","no auto merge / deploy"];
    byId("overviewSignals").innerHTML = '<div class="signalRow">'+signals.map(s=>'<span class="signal">◇ '+safe(s)+'</span>').join("")+"</div>";
  }
  function renderSystems() {
    const filter = byId("systemFilter").value;
    const entries = model.systems.filter(s => filter === "all" || s.status === filter);
    byId("systemsGrid").innerHTML = entries.map(s=>'<article class="tile"><div class="tileTop"><span class="tinyId">'+safe(s.id)+'</span>'+statusBadge(s.status)+'</div><h3>'+safe(s.title)+'</h3><p>'+safe(s.summary)+'</p><p><b>Next proof:</b> '+safe(s.proof)+'</p>'+sourceAnchor(s.evidence)+'</article>').join("") || '<p>No matching systems.</p>';
  }
  function renderAssets() {
    const query = byId("assetSearch").value.trim().toLowerCase();
    const entries = model.assets.filter(a => [a.id,a.name,a.lane,a.rights,a.next].join(" ").toLowerCase().includes(query));
    byId("assetRows").innerHTML = entries.map(a=>'<tr><td><strong>'+safe(a.name)+'</strong><small>'+safe(a.id)+'</small>'+sourceAnchor(a.evidence)+'</td><td>'+safe(a.lane)+'</td><td>'+statusBadge(a.status)+'</td><td>'+safe(a.rights)+'</td><td>'+safe(a.next)+'</td></tr>').join("") || '<tr><td colspan="5">No matching assets.</td></tr>';
  }
  function renderAgents() {
    byId("agentGrid").innerHTML = model.agents.map(a=>'<div class="agentCard"><strong>'+safe(a.id)+'</strong><small>'+safe(a.role)+'</small><small>'+safe(label(a.state))+'</small></div>').join("");
  }
  function renderChecklist() {
    const done = model.compliance.filter(c=>!!state.checked[c.id]).length;
    byId("checklistProgress").textContent = done + " / " + model.compliance.length + " reviewed locally";
    byId("checklistRows").innerHTML = model.compliance.map(c=>'<div class="checkRow"><input type="checkbox" id="check-'+safe(c.id)+'" data-check="'+safe(c.id)+'" '+(state.checked[c.id]?"checked":"")+' aria-label="Review '+safe(c.label)+'"><div><label for="check-'+safe(c.id)+'"><strong>'+safe(c.label)+'</strong></label><p>'+safe(c.details)+'</p></div>'+sourceAnchor(c.evidence)+'</div>').join("");
  }
  function gapState(g) { return state.gaps[g.id] || {status:g.status,note:g.note || ""}; }
  function renderGaps() {
    const filter = byId("gapFilter").value;
    const entries = model.gaps.filter(g=>filter === "all" || gapState(g).status === filter);
    byId("gapRows").innerHTML = entries.map(g=>{
      const v=gapState(g);
      return '<article class="gapCard"><div><span class="tinyId">'+safe(g.id)+' / '+safe(g.systemId)+'</span><h3>'+safe(g.title)+'</h3><p><b>Next proof:</b> '+safe(g.next)+'</p></div><div><label for="gapState-'+safe(g.id)+'">LOCAL TRIAGE STATE</label><select id="gapState-'+safe(g.id)+'" data-gap-status="'+safe(g.id)+'">'+statuses.map(s=>'<option value="'+s+'" '+(s===v.status?"selected":"")+'>'+safe(label(s))+'</option>').join("")+'</select></div><div><label for="gapNote-'+safe(g.id)+'">EVIDENCE / HANDOFF NOTE</label><textarea id="gapNote-'+safe(g.id)+'" data-gap-note="'+safe(g.id)+'" placeholder="Exact sourceRef, receipt, blocker, next action…">'+safe(v.note)+'</textarea></div></article>';
    }).join("") || '<p>No matching gaps.</p>';
  }
  function renderAudit() {
    byId("auditStages").innerHTML = model.auditStages.map((a,i)=>{
      const selected = a.id === "deploy" ? "blocked" : (state.audits[a.id] || a.state);
      return '<article class="auditStep"><div class="auditNumber">STAGE '+String(i+1).padStart(2,"0")+'</div><h3>'+safe(a.id)+'</h3><p>'+safe(a.task)+'</p><label class="tinyId" for="audit-'+safe(a.id)+'">LOCAL CHECKPOINT ONLY</label><select id="audit-'+safe(a.id)+'" data-audit="'+safe(a.id)+'" '+(a.id==="deploy"?"disabled title=\"Requires separate human and host approvals\"":"")+'>'+auditStates.map(s=>'<option value="'+s+'" '+(s===selected?"selected":"")+'>'+safe(label(s))+'</option>').join("")+'</select></article>';
    }).join("");
  }
  function renderDeploy() {
    byId("deployGrid").innerHTML=model.deploy.map(d=>'<article class="tile"><div class="tileTop"><span class="tinyId">'+safe(d.id)+'</span>'+statusBadge(d.status)+'</div><h3>'+safe(d.title)+'</h3><p>'+safe(d.body)+'</p>'+sourceAnchor(d.evidence)+'</article>').join("");
    byId("installActions").innerHTML=model.installActions.map(a=>'<li><strong>'+safe(a.title)+'</strong><small>'+safe(a.detail)+'</small></li>').join("");
  }
  function renderAll() {renderMetrics();renderOverview();renderSystems();renderAssets();renderAgents();renderChecklist();renderGaps();renderAudit();renderDeploy();}
  function setView(name) {
    if (!viewIds.includes(name)) return;
    activeView=name;
    for(const button of document.querySelectorAll("[data-view]")) {
      const current=button.dataset.view===name;
      button.classList.toggle("isActive",current);
      button.setAttribute("aria-current",current?"page":"false");
    }
    for(const id of viewIds) byId("panel-"+id).classList.toggle("isVisible",id===name);
    byId("workspace").scrollIntoView({behavior:"instant",block:"start"});
    history.replaceState(null,"","#"+name);
  }
  function stepView(delta) {setView(viewIds[(viewIds.indexOf(activeView)+delta+viewIds.length)%viewIds.length]);}
  function exportState() {
    const payload={...state,exportedAt:new Date().toISOString(),baseline:{schema:model.schema,sourceRef:model.sourceRef,canonAuthorityPath:model.canonAuthorityPath,canonicalRepository:model.canonicalRepository}};
    const blob=new Blob([JSON.stringify(payload,null,2)+"\n"],{type:"application/json"});
    const url=URL.createObjectURL(blob);
    const a=document.createElement("a"); a.href=url; a.download="canonControlRoom-localState.json";document.body.append(a);a.click();a.remove();URL.revokeObjectURL(url);
    notice("Exported local triage. Commit only reviewed, sanitized changes via GitHub PR.");
  }
  async function importState(file) {
    if (!file) return;
    if (file.size > 1024 * 1024) {notice("Import rejected: JSON file exceeds 1 MiB.");return;}
    try {
      const incoming=JSON.parse(await file.text());
      if (incoming.schema!==localSchema) throw new Error("wrong schema");
      if (incoming.baseline?.canonicalRepository && incoming.baseline.canonicalRepository!==model.canonicalRepository) throw new Error("different repository");
      const cleaned=cleanState(incoming);
      state=cleanState({schema:localSchema,checked:{...state.checked,...cleaned.checked},gaps:{...state.gaps,...cleaned.gaps},audits:{...state.audits,...cleaned.audits},history:[...state.history,...cleaned.history]});
      store("imported sanitized local review state");
      renderAll();
      notice("Imported and merged review state locally. Existing unrelated keys were preserved.");
    } catch (error) {notice("Import rejected. Expected this app's versioned local-state JSON, not a Canon authority file.");}
  }
  function bindEvents() {
    byId("viewNav").addEventListener("click",e=>{const button=e.target.closest("[data-view]");if(button)setView(button.dataset.view);});
    byId("navPrevious").addEventListener("click",()=>stepView(-1));
    byId("navNext").addEventListener("click",()=>stepView(1));
    byId("exportButton").addEventListener("click",exportState);
    byId("importFile").addEventListener("change",async e=>{await importState(e.target.files?.[0]);e.target.value="";});
    byId("systemFilter").addEventListener("change",renderSystems);
    byId("assetSearch").addEventListener("input",renderAssets);
    byId("gapFilter").addEventListener("change",renderGaps);
    byId("checklistRows").addEventListener("change",e=>{const id=e.target.dataset.check;if(!id)return;state.checked[id]=e.target.checked;store("checklist "+id+" locally reviewed="+e.target.checked);renderChecklist();});
    byId("gapRows").addEventListener("change",e=>{
      const s=e.target.dataset.gapStatus, n=e.target.dataset.gapNote, id=s||n;
      if (!id || !model.gaps.some(g=>g.id===id)) return;
      const baseline=model.gaps.find(g=>g.id===id), current=gapState(baseline);
      if (s && statuses.includes(e.target.value)) current.status=e.target.value;
      if (n) current.note=e.target.value.slice(0,2500);
      state.gaps[id]=current;
      store("gap "+id+" local "+(s?"status":"note")+" changed");
      if (s && byId("gapFilter").value!=="all") renderGaps();
    });
    byId("auditStages").addEventListener("change",e=>{const id=e.target.dataset.audit; if(!id||id==="deploy"||!auditStates.includes(e.target.value))return;state.audits[id]=e.target.value;store("audit "+id+" local stage="+e.target.value);});
    document.addEventListener("keydown",e=>{
      if(!e.altKey || !["ArrowUp","ArrowDown"].includes(e.key) || /input|textarea|select/i.test(e.target.tagName)) return;
      e.preventDefault();stepView(e.key==="ArrowUp"?-1:1);
    });
    let startY=null;
    const rail=byId("navRail");
    rail.addEventListener("touchstart",e=>{startY=e.touches.length===1?e.touches[0].clientY:null;},{passive:true});
    rail.addEventListener("touchend",e=>{if(startY===null)return;const dy=e.changedTouches[0].clientY-startY;startY=null;if(Math.abs(dy)>=42)stepView(dy<0?1:-1);},{passive:true});
  }
  async function init() {
    bindEvents();
    try {
      const response=await fetch("./canonSnapshotV1.json",{cache:"no-store"});
      if (!response.ok) throw new Error("HTTP "+response.status);
      model=await response.json();
      if(model.schema!=="luhmOs.canonControlRoomSnapshot.v1" || model.canonicalRepository!=="eggie-admin/LuHm-OS") throw new Error("invalid source snapshot");
      try {state=cleanState(JSON.parse(localStorage.getItem(storageKey)||"null"));} catch {state=cleanState(null);}
      byId("snapshotStamp").textContent="Source inspection "+model.snapshotAt+" · not a live GitHub feed";
      renderAll();setView(viewIds.includes(location.hash.slice(1))?location.hash.slice(1):"overview");
    } catch(error) {
      notice("Snapshot failed to load. Serve this folder over local HTTP: python3 -m http.server 8765 --directory sites/canon-control-room. No network or plugin connection is required.");
    }
  }
  document.addEventListener("DOMContentLoaded",init);
})();