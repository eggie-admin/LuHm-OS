(function (root) {
  "use strict";
  const schema = "luhmOs.samsungArtDesk.v1";
  const slotIds = Object.freeze(["100", "200", "300", "401", "402", "403", "500"]);
  const speakers = new Set(["lum", "urd", "belldandy", "skuld", "yume", "professor", "none"]);
  const maxStrokes = 360, maxPoints = 20000, maxBytes = 1024 * 1024;
  const colorPattern = /^#[0-9a-fA-F]{6}$/;
  const cleanText = (v, limit, fallback) => typeof v === "string" && v.trim() && v.length <= limit ? v : fallback;
  function countPoints(packet) {
    return packet.shots.reduce((sum, shot) => sum + shot.strokes.reduce((n, stroke) => n + stroke.points.length, 0), 0);
  }
  function appendPoint(stroke, next, remainingBudget) {
    if (remainingBudget <= 0 || stroke.points.length >= 2000) return false;
    const last = stroke.points[stroke.points.length - 1];
    if (last[0] === next[0] && last[1] === next[1]) return false;
    stroke.points.push(next);
    return true;
  }
  function blankShot(slot) { return {slot, notes:"", speaker:"none", strokes:[]}; }
  function fresh() {
    return {schema, project:"into-the-warp", artist:"Professor", sourceRef:"UNKNOWN",
      approved:false, serverWrites:false, shots:slotIds.map(blankShot)};
  }
  function cleanPacket(value) {
    if (!value || typeof value !== "object" || Array.isArray(value) || value.schema !== schema ||
        value.approved !== false || value.serverWrites !== false ||
        !Array.isArray(value.shots) || value.shots.length !== slotIds.length) throw Error("Invalid storyboard contract");
    let total = 0;
    const shots = value.shots.map((shot, index) => {
      if (!shot || shot.slot !== slotIds[index] || typeof shot.notes !== "string" || shot.notes.length > 1200 ||
          !speakers.has(shot.speaker) || !Array.isArray(shot.strokes) || shot.strokes.length > maxStrokes) throw Error("Invalid shot");
      const strokes = shot.strokes.map(stroke => {
        if (!stroke || typeof stroke !== "object" || !colorPattern.test(stroke.color) ||
            !Number.isInteger(stroke.width) || stroke.width < 1 || stroke.width > 24 ||
            typeof stroke.erase !== "boolean" || !Array.isArray(stroke.points) ||
            stroke.points.length < 1 || stroke.points.length > 2000) throw Error("Invalid stroke");
        total += stroke.points.length;
        if (total > maxPoints) throw Error("Too many points");
        return {color:stroke.color, width:stroke.width, erase:stroke.erase,
          points:stroke.points.map(p => {
            if (!Array.isArray(p) || p.length !== 2 || !p.every(Number.isInteger) ||
                p[0] < 0 || p[0] > 720 || p[1] < 0 || p[1] > 405) throw Error("Invalid coordinate");
            return [p[0],p[1]];
          })};
      });
      return {slot:slotIds[index], notes:shot.notes, speaker:shot.speaker, strokes};
    });
    if (typeof value.project !== "string" || !value.project.trim() || value.project.length > 80 ||
        typeof value.artist !== "string" || !value.artist.trim() || value.artist.length > 60 ||
        typeof value.sourceRef !== "string" ||
        !(value.sourceRef === "UNKNOWN" || /^[0-9a-f]{40}$/.test(value.sourceRef))) throw Error("Invalid identity");
    return {schema, project:value.project, artist:value.artist, sourceRef:value.sourceRef,
      approved:false, serverWrites:false, shots};
  }
  function sanitizedDownload(doc, filename, data, type) {
    const url = root.URL.createObjectURL(new Blob([data], {type}));
    const a = doc.createElement("a"); a.href=url; a.download=filename;
    doc.body.append(a); a.click(); a.remove();
    root.setTimeout(() => root.URL.revokeObjectURL(url), 8000);
  }
  function mount(doc) {
    const get = id => doc.getElementById(id);
    const canvas=get("samsung-canvas"), status=get("samsung-status");
    if (!canvas || !status || !canvas.getContext || canvas.dataset.wired) return false;
    canvas.dataset.wired = "true";
    const context=canvas.getContext("2d");
    if (!context) {status.textContent="This browser cannot open the drawing canvas.";return false;}
    let packet=fresh(), active=0, drawing=null, tool="pen", changed=false, pointBudget=0;
    const announce = text => {status.textContent=text;};
    function renderCanvas() {
      context.clearRect(0,0,720,405);
      for (const stroke of packet.shots[active].strokes) {
        context.save();context.globalCompositeOperation=stroke.erase?"destination-out":"source-over";
        context.strokeStyle=stroke.color;context.fillStyle=stroke.color;context.lineWidth=stroke.width;
        context.lineCap="round";context.lineJoin="round";
        const pts=stroke.points;context.beginPath();context.moveTo(pts[0][0],pts[0][1]);
        if (pts.length===1) {context.arc(pts[0][0],pts[0][1],stroke.width/2,0,Math.PI*2);context.fill();}
        else {for(let i=1;i<pts.length;i++)context.lineTo(pts[i][0],pts[i][1]);context.stroke();}
        context.restore();
      }
    }
    function renderShots() {
      const area=get("samsung-shots");area.replaceChildren();
      packet.shots.forEach((shot,index)=>{
        const button=doc.createElement("button");button.type="button";
        button.textContent=shot.slot+(shot.strokes.length?" •":"");
        button.setAttribute("aria-pressed",String(active===index));
        button.addEventListener("click",()=>{if(drawing)return;active=index;renderShots();renderDetails();});
        area.append(button);
      });
    }
    function renderDetails() {
      get("samsung-notes").value=packet.shots[active].notes;
      get("samsung-speaker").value=packet.shots[active].speaker;
      renderCanvas();
    }
    function point(event) {
      const rect=canvas.getBoundingClientRect();
      return [Math.max(0,Math.min(720,Math.round((event.clientX-rect.left)*720/rect.width))),
        Math.max(0,Math.min(405,Math.round((event.clientY-rect.top)*405/rect.height)))];
    }
    canvas.addEventListener("pointerdown",event=>{
      if(event.button!==0 && event.pointerType==="mouse")return;
      const current=packet.shots[active];
      if(current.strokes.length>=maxStrokes)return announce("This shot has reached its stroke limit. Export a copy.");
      if(pointBudget>=maxPoints)return announce("Point limit reached. Export a copy.");
      drawing={color:get("samsung-color").value,width:Number(get("samsung-width").value),
        erase:tool==="eraser",points:[point(event)]};
      current.strokes.push(drawing);pointBudget++;canvas.setPointerCapture(event.pointerId);
      renderCanvas();changed=true;
    });
    canvas.addEventListener("pointermove",event=>{
      if(!drawing || !canvas.hasPointerCapture(event.pointerId))return;
      if(!appendPoint(drawing,point(event),maxPoints-pointBudget))return;
      pointBudget++;renderCanvas();
    });
    function finish(){if(!drawing)return;drawing=null;renderShots();announce("Local drawing changed. Export before leaving.");}
    canvas.addEventListener("pointerup",finish);
    canvas.addEventListener("pointercancel",finish);
    canvas.addEventListener("lostpointercapture",finish);
    for(const t of ["pen","eraser"])get("samsung-"+t).addEventListener("click",()=>{
      tool=t;for(const x of ["pen","eraser"])get("samsung-"+x).setAttribute("aria-pressed",String(x===t));
    });
    get("samsung-undo").addEventListener("click",()=>{
      const undone=packet.shots[active].strokes.pop();
      if(undone){pointBudget-=undone.points.length;changed=true;renderCanvas();renderShots();announce("Last stroke removed. Export to preserve changes.");}
    });
    get("samsung-clear").addEventListener("click",()=>{
      if(!packet.shots[active].strokes.length)return;
      if(!root.confirm("Clear only this shot? Your exported files will remain unchanged."))return;
      pointBudget-=packet.shots[active].strokes.reduce((sum,stroke)=>sum+stroke.points.length,0);
      packet.shots[active].strokes=[];changed=true;renderCanvas();renderShots();announce("Shot cleared locally.");
    });
    get("samsung-notes").addEventListener("input",event=>{packet.shots[active].notes=event.target.value.slice(0,1200);changed=true;});
    get("samsung-speaker").addEventListener("change",event=>{packet.shots[active].speaker=event.target.value;changed=true;});
    const syncNames=()=>{
      packet.project=cleanText(get("samsung-project").value,80,packet.project);
      packet.artist=cleanText(get("samsung-artist").value,60,packet.artist);
    };
    get("samsung-save").addEventListener("click",()=>{
      syncNames();
      const safe=cleanPacket(packet);
      const slug=safe.project.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"").slice(0,44)||"art";
      sanitizedDownload(doc,slug+"-storyboard-candidate.json",JSON.stringify(safe,null,2)+"\n","application/json");
      changed=false;announce("Editable storyboard exported. Use approved private Drive for teammate handoff; there is no live sync.");
    });
    get("samsung-png").addEventListener("click",()=>{
      const out=doc.createElement("canvas");out.width=720;out.height=405;const ctx=out.getContext("2d");
      ctx.fillStyle="#ffffff";ctx.fillRect(0,0,720,405);ctx.drawImage(canvas,0,0);
      out.toBlob(blob=>{
        if(!blob)return announce("PNG export is not supported in this browser.");
        const url=root.URL.createObjectURL(blob),a=doc.createElement("a");a.href=url;
        a.download="shot-"+packet.shots[active].slot+"-candidate.png";doc.body.append(a);a.click();a.remove();
        root.setTimeout(()=>root.URL.revokeObjectURL(url),8000);
        announce("Shot PNG exported. Canvas draft remains editable in this session.");
      },"image/png");
    });
    get("samsung-import").addEventListener("change",async event=>{
      const file=event.target.files?.[0];event.target.value="";
      if(!file)return;
      if(file.size>maxBytes)return announce("Import refused: storyboard JSON exceeds 1 MiB.");
      try {
        const parsed=cleanPacket(JSON.parse(await file.text()));
        if(changed && !root.confirm("Replace the current unsaved storyboard with this team handoff?"))return;
        packet=parsed;active=0;drawing=null;changed=false;pointBudget=countPoints(packet);
        get("samsung-project").value=packet.project;get("samsung-artist").value=packet.artist;
        renderShots();renderDetails();announce("Editable team storyboard imported locally. No files uploaded.");
      }catch(_){announce("Import rejected: invalid or unsafe storyboard JSON.");}
    });
    root.addEventListener("beforeunload",event=>{if(changed){event.preventDefault();event.returnValue="";}});
    renderShots();renderDetails();announce("Touch or draw with a pen. Your work stays on this device until exported.");
    return true;
  }
  const api={schema,slotIds,cleanPacket,fresh,countPoints,appendPoint,mount};
  if(typeof module==="object" && module.exports)module.exports=api;
  root.LuHmSamsungArtDesk=api;
  if(root.document){
    if(root.document.readyState==="loading")root.document.addEventListener("DOMContentLoaded",()=>mount(root.document),{once:true});
    else mount(root.document);
  }
})(typeof window!=="undefined"?window:globalThis);
