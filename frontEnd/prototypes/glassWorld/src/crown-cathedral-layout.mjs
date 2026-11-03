/* LuHm-OS Crown Cathedral: pure bounded environment layout, no IO or authority. */
export const crownModes = Object.freeze(["cathedral", "riverwalk", "workshop"]);
export const crownLayoutSchema = "luhmOs.crownCathedralLayout.v1";
const clamp = n => Math.round(n * 1000) / 1000;
const allowed = new Set(["box","sphere","cylinder","torus"]);
function part(id, kind, x, y, z, sx, sy, sz, color, glow = false) {
  if (!allowed.has(kind) || !/^[a-z0-9-]{1,48}$/.test(id)) throw Error("RED_CROWN_PART");
  const numbers = [x,y,z,sx,sy,sz];
  if (numbers.some(v=>!Number.isFinite(v) || Math.abs(v)>18) || [sx,sy,sz].some(v=>v<=0||v>18))
    throw Error("RED_CROWN_GEOMETRY");
  if (!/^#[0-9a-f]{6}$/.test(color)) throw Error("RED_CROWN_COLOR");
  return {id,kind,position:{x:clamp(x),y:clamp(y),z:clamp(z)},
    size:{x:clamp(sx),y:clamp(sy),z:clamp(sz)},color,glow};
}
export function buildCrownLayout(mode="cathedral") {
  if (!crownModes.includes(mode)) throw Error("RED_CROWN_MODE");
  const parts=[],add=(...args)=>parts.push(part(...args));
  // Composition is illustrative 3D geometry, NOT a rigged/animated Lum model.
  if (mode==="cathedral") {
    add("dais","cylinder",0,-.92,-2.8,3.0,.40,3.0,"#574070");
    add("aisle","box",0,-1.24,.2,5.8,.22,14.5,"#201e43");
    for (let i=0;i<5;i++){
      const z=-5+i*2.5;
      add("step-"+i,"box",0,-1.08,z,2.8,.035,1.0,i%2?"#643e75":"#21455e");
      for (const side of [-1,1]) {
        const code=(side<0?"l":"r")+"-"+i;
        add("base-"+code,"box",side*3.05,-.89,z,.82,.42,.83,"#443c68");
        add("pillar-"+code,"cylinder",side*3.05,.45,z,.46,2.5,.46,"#39365b");
        add("capital-"+code,"box",side*3.05,1.75,z,.95,.28,.9,"#87538b");
        add("spire-"+code,"cylinder",side*3.05,2.25,z,.54,1.0,.54,"#a35b9f",true);
      }
      add("lintel-"+i,"box",0,2.05,z,6.3,.20,.42,"#764a83");
      add("arch-"+i,"torus",0,2.02,z,.65,.65,.65,"#f274dc",true);
    }
    for(const side of [-1,1])for(let i=0;i<5;i++) {
      const z=-4.7+i*2.45;
      add("glass-"+(side<0?"l":"r")+"-"+i,"box",side*3.8,.35,z,.11,1.9,.86,i%2?"#00b5c8":"#a945cb",true);
    }
    add("rose","torus",0,1.95,-7.65,2.0,2.0,.30,"#e35fce",true);
  } else if (mode==="riverwalk") {
    add("pavement","box",0,-1.23,0,9.5,.22,13,"#273249");
    add("river","box",-4,-1.13,0,2,.03,13,"#116987",true);
    for(let i=0;i<7;i++){
      const z=-5.4+i*1.8;
      add("streetlight-post-"+i,"cylinder",2.8,.0,z,.13,2.4,.13,"#464a6d");
      add("streetlight-glow-"+i,"sphere",2.8,1.25,z,.36,.36,.36,"#9bffff",true);
      add("riverwalk-brick-"+i,"box",4.1,-.8,z,1.4,.7,1.35,"#5a345a");
    }
    for(let i=0;i<5;i++)add("billboard-"+i,"box",4.1,1.15,-4.5+i*2.3,1.2,1.5,.15,i%2?"#ec4c9a":"#48aac8",true);
  } else {
    add("studio-floor","box",0,-1.2,0,9,.2,12,"#263351");
    add("backdrop","box",0,1.5,-5.6,8,5,.18,"#302557");
    add("studio-ring","torus",0,1.0,-5.4,2.2,2.2,.2,"#d455be",true);
    for(const side of [-1,1]){
      add("rig-"+(side<0?"l":"r"),"cylinder",side*3.2,.4,-1.3,.24,3,.24,"#7889a3");
      add("softbox-"+(side<0?"l":"r"),"box",side*3.2,1.75,-1.3,.9,1.0,.35,"#80f5f7",true);
      add("console-"+(side<0?"l":"r"),"box",side*2.4,-.75,2,1.4,.8,1.3,"#485578");
    }
  }
  // 3D proxy only. Source-to-rigged model and original character likeness need separate proof.
  add("proxy-shadow","cylinder",0,-.97,-2.55,.9,.04,.9,"#1b102c");
  add("proxy-coat","cylinder",0,-.22,-2.55,.90,1.36,.72,"#64327f");
  add("proxy-head","sphere",0,.83,-2.55,.83,.91,.82,"#f4c7da");
  add("proxy-hair","sphere",0,1.14,-2.63,.91,.77,.87,"#211831");
  for(const side of [-1,1]){
    const t=side<0?"l":"r";
    add("proxy-horn-"+t,"cylinder",side*.32,1.84,-2.65,.23,.59,.23,"#f17bcf",true);
    add("proxy-eye-"+t,"sphere",side*.20,.77,-2.11,.10,.13,.05,"#a352cd",true);
    add("proxy-arm-"+t,"cylinder",side*.61,-.20,-2.53,.22,.95,.22,"#5b326e");
  }
  add("proxy-heart","sphere",0,-.04,-2.04,.21,.23,.11,"#f97cdb",true);
  if (parts.length>128 || new Set(parts.map(x=>x.id)).size!==parts.length) throw Error("RED_CROWN_BUDGET");
  return {schema:crownLayoutSchema,mode,parts,
    attribution:"Procedural original 3D proxy, NOT the approved rigged/Live2D Canon Lum asset",
    runtimeAuthority:false,publicationAuthority:false};
}
