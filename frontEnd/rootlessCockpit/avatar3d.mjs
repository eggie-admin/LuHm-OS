/* LuHm-OS original adult goth oni: procedural WebGL2 preview.
 * No CDN, third-party assets, downloaded meshes, root or AI calls.
 * This is animated proxy geometry, not an inspected/rigged Blender asset.
 */
export const AVATAR_INFO = Object.freeze({
  schema:"luhmOs.originalAdultGothAvatarPreview.v1",
  character:"original-adult-goth-oni",
  adult:true, renderer:"nativeWebGL2", rigged:false, nativeApk:false,
  source:"original-procedural", maxTriangles:18000,
  aesthetic:"gothic-anime", outfit:"opaque-corseted-velvet",
  assetDownloads:0, modelTraining:false
});
const C={
 skin:[0.87,0.64,0.69], shadow:[0.72,0.46,0.56], blush:[0.97,0.52,0.69],
 hair:[0.07,0.055,0.13], hairLite:[0.14,0.09,0.20],
 velvet:[0.17,0.075,0.26], bodice:[0.25,0.10,0.35], seam:[0.72,0.31,0.63],
 lace:[0.93,0.59,0.82], metal:[0.76,0.56,0.92], iris:[0.84,0.29,0.91],
 eye:[0.96,0.88,0.96], ink:[0.11,0.045,0.18], gem:[0.91,0.24,0.58],
 boot:[0.085,0.055,0.145]
};
const V=(x,y,z)=>[x,y,z];
function ellipsoid(data,label,center,radius,color,roll=0,rings=12,segments=18){
  const [cx,cy,cz]=center,[rx,ry,rz]=radius;
  const offset=data.positions.length/3,cr=Math.cos(roll),sr=Math.sin(roll);
  for(let r=0;r<=rings;r++){
    const th=Math.PI*r/rings,st=Math.sin(th),ct=Math.cos(th);
    for(let s=0;s<=segments;s++){
      const ph=2*Math.PI*s/segments,a=st*Math.cos(ph),b=ct,c=st*Math.sin(ph);
      const x=a*rx,y=b*ry,z=c*rz;
      data.positions.push(cx+x*cr-y*sr,cy+x*sr+y*cr,cz+z);
      let nx=a/rx,ny=b/ry,nz=c/rz;
      const nx2=nx*cr-ny*sr,ny2=nx*sr+ny*cr;
      const n=Math.hypot(nx2,ny2,nz)||1;
      data.normals.push(nx2/n,ny2/n,nz/n);
      data.colors.push(...color);
    }
  }
  for(let r=0;r<rings;r++)for(let s=0;s<segments;s++){
    const a=offset+r*(segments+1)+s,b=a+segments+1;
    data.indices.push(a,b,a+1,b,b+1,a+1);
  }
  data.parts.push(label);
}
function cone(data,label,x,y,z,radius,height,color,bend=0,segments=18){
  const offset=data.positions.length/3,rings=7;
  for(let r=0;r<=rings;r++){
    const t=r/rings,R=radius*Math.pow(1-t,0.83)+0.002;
    for(let s=0;s<=segments;s++){
      const ph=2*Math.PI*s/segments,cos=Math.cos(ph),sin=Math.sin(ph);
      data.positions.push(x+bend*t*t+R*cos,y+height*t,z+R*sin);
      const norm=Math.hypot(cos,0.28,sin);
      data.normals.push(cos/norm,0.28/norm,sin/norm);
      data.colors.push(...color);
    }
  }
  for(let r=0;r<rings;r++)for(let s=0;s<segments;s++){
    const a=offset+r*(segments+1)+s,b=a+segments+1;
    data.indices.push(a,a+1,b,a+1,b+1,b);
  }
  data.parts.push(label);
}
function skirt(data){
  const offset=data.positions.length/3,segments=32,rings=10;
  for(let r=0;r<=rings;r++){
    const t=r/rings,rad=0.40+0.55*t;
    for(let s=0;s<=segments;s++){
      const a=s/segments*Math.PI*2,x=Math.cos(a),z=Math.sin(a);
      const scallop=(.018*Math.sin(a*8+.4))*t;
      data.positions.push(rad*x,-.56-1.02*t+scallop,0.05+rad*.54*z);
      const norm=Math.hypot(x,.2,z);
      data.normals.push(x/norm,.2/norm,z/norm);
      data.colors.push(...(s%4===0?C.bodice:C.velvet));
    }
  }
  for(let r=0;r<rings;r++)for(let s=0;s<segments;s++){
    const a=offset+r*(segments+1)+s,b=a+segments+1;
    data.indices.push(a,b,a+1,b,b+1,a+1);
  }
  data.parts.push("pleated-velvet-skirt");
}
export function createAvatarGeometry(){
  const d={positions:[],normals:[],colors:[],indices:[],parts:[]};
  // All skin areas stay fully clothed apart from face, neck and hands.
  for(const sign of [-1,1]){
    ellipsoid(d,"thigh"+sign,V(sign*.29,-1.34,0),V(.23,.58,.23),C.shadow,sign*-.05);
    ellipsoid(d,"overknee-boot"+sign,V(sign*.30,-1.73,.02),V(.22,.47,.24),C.boot);
    ellipsoid(d,"shoe"+sign,V(sign*.30,-2.03,.20),V(.24,.14,.38),C.ink);
  }
  skirt(d);
  ellipsoid(d,"corset-torso",V(0,-.04,0),V(.57,.81,.37),C.velvet);
  ellipsoid(d,"front-bodice",V(0,.22,.29),V(.53,.52,.20),C.bodice);
  for(const sign of [-1,1]){
    ellipsoid(d,"opaque-bust-panel"+sign,V(sign*.29,.44,.39),V(.385,.38,.34),C.bodice,sign*.10);
    ellipsoid(d,"corset-seam"+sign,V(sign*.21,-.01,.47),V(.025,.42,.026),C.seam,sign*.24,8,12);
    ellipsoid(d,"puff-sleeve"+sign,V(sign*.70,.48,0),V(.28,.35,.32),C.velvet,sign*.28);
    ellipsoid(d,"arm"+sign,V(sign*.88,-.06,0),V(.19,.45,.19),C.bodice,sign*.18);
    ellipsoid(d,"glove"+sign,V(sign*.93,-.50,.04),V(.15,.15,.16),C.skin);
  }
  ellipsoid(d,"heart-brooch",V(0,.47,.77),V(.13,.16,.065),C.gem);
  ellipsoid(d,"necklace",V(0,.92,.33),V(.20,.065,.10),C.metal);
  ellipsoid(d,"neck",V(0,1.05,0),V(.22,.26,.23),C.skin);
  // Hair is assembled before face so the eyes are visible from the front.
  ellipsoid(d,"back-hair",V(0,1.32,-.23),V(.66,.99,.38),C.hair);
  for(const sign of [-1,1]){
    ellipsoid(d,"long-side-hair"+sign,V(sign*.57,1.05,.06),V(.18,.78,.26),C.hairLite,sign*.12);
    ellipsoid(d,"ear"+sign,V(sign*.51,1.51,.02),V(.16,.17,.13),C.skin);
  }
  ellipsoid(d,"face",V(0,1.58,.18),V(.49,.60,.40),C.skin);
  ellipsoid(d,"hair-crown",V(0,2.08,.01),V(.58,.25,.42),C.hair);
  for(const sign of [-1,1]){
    cone(d,"curved-oni-horn"+sign,sign*.37,2.20,-.05,.17,.45,C.metal,sign*.18);
    ellipsoid(d,"swept-bang"+sign,V(sign*.22,1.98,.47),V(.28,.11,.10),C.hair,sign*.24,10,18);
    ellipsoid(d,"eyeliner"+sign,V(sign*.20,1.61,.542),V(.19,.115,.055),C.ink,sign*.04,10,18);
    ellipsoid(d,"eyeball"+sign,V(sign*.20,1.61,.593),V(.155,.075,.039),C.eye,sign*.02,10,18);
    ellipsoid(d,"iris"+sign,V(sign*.20,1.60,.624),V(.062,.066,.031),C.iris,0,10,14);
    ellipsoid(d,"eyelight"+sign,V(sign*.18,1.63,.650),V(.024,.024,.010),C.eye,0,8,10);
    ellipsoid(d,"brow"+sign,V(sign*.22,1.79,.53),V(.16,.028,.031),C.hair,sign*.10,8,12);
  }
  ellipsoid(d,"nose",V(0,1.44,.576),V(.055,.10,.056),C.shadow,0,10,12);
  ellipsoid(d,"rose-lips",V(0,1.29,.557),V(.14,.046,.045),C.blush,0,10,16);
  ellipsoid(d,"chin",V(0,1.17,.49),V(.19,.085,.075),C.skin);
  const vertexCount=d.positions.length/3,triangles=d.indices.length/3;
  if(vertexCount>45000||triangles>AVATAR_INFO.maxTriangles||!d.positions.every(Number.isFinite)||
      d.indices.some(i=>!Number.isInteger(i)||i<0||i>=vertexCount))throw Error("INVALID_AVATAR_GEOMETRY");
  return {positions:new Float32Array(d.positions),normals:new Float32Array(d.normals),
    colors:new Float32Array(d.colors),indices:new Uint32Array(d.indices),parts:d.parts,
    vertexCount,triangles,editableMaster:false,modelDownloaded:false,rigged:false};
}
const VERTEX=`#version 300 es
precision highp float;
layout(location=0) in vec3 aPosition;
layout(location=1) in vec3 aNormal;
layout(location=2) in vec3 aColor;
uniform mat4 uProjection;
uniform float uYaw;
uniform float uBreath;
out vec3 vColor;
out float vShade;
void main(){
 float co=cos(uYaw),si=sin(uYaw);
 vec3 p=aPosition;
 p.y += uBreath*0.016*smoothstep(-0.7,0.9,p.y);
 mat3 rot=mat3(co,0.,-si, 0.,1.,0., si,0.,co);
 vec3 n=normalize(rot*aNormal);
 p=rot*p;
 p.y-=0.25;
 p.z-=5.9;
 gl_Position=uProjection*vec4(p,1.0);
 float diffuse=max(dot(n,normalize(vec3(-0.42,0.75,0.61))),0.0);
 vShade=0.38+0.62*diffuse;
 vColor=aColor;
}`;
const FRAGMENT=`#version 300 es
precision highp float;
in vec3 vColor;
in float vShade;
out vec4 outColor;
void main(){
 vec3 color=pow(vColor*vShade,vec3(0.92));
 outColor=vec4(color,1.0);
}`;
function compile(gl,type,src){
  const shader=gl.createShader(type);
  if(!shader)throw Error("SHADER_ALLOC");
  gl.shaderSource(shader,src);gl.compileShader(shader);
  if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS)){
    gl.deleteShader(shader);throw Error("SHADER_COMPILE");
  }
  return shader;
}
export function mountAvatarPreview(canvas,fallback,report){
  if(!canvas||typeof canvas.getContext!=="function")return {status:"FALLBACK",dispose(){}};
  let gl;
  try{gl=canvas.getContext("webgl2",{antialias:true,alpha:true,premultipliedAlpha:false,powerPreference:"low-power"});}catch{}
  if(!gl){if(report)report.textContent="3D unavailable · original 2D artwork";return {status:"FALLBACK",dispose(){}};}
  let program,buffer,colorBuffer,indexBuffer,normalBuffer,frame=0,last=0,disposed=false,yaw=-.26,drag=null;
  const onContextLoss=e=>{e.preventDefault();dispose();canvas.hidden=true;if(fallback)fallback.hidden=false;if(report)report.textContent="3D paused · 2D fallback";};
  const pointerDown=e=>{drag=e.clientX;canvas.setPointerCapture?.(e.pointerId);};
  const pointerMove=e=>{if(drag===null)return;const delta=e.clientX-drag;drag=e.clientX;yaw+=Math.max(-0.12,Math.min(.12,delta*.008));};
  const pointerUp=()=>{drag=null;};
  const key=e=>{if(e.key==="ArrowLeft"||e.key==="ArrowRight"){e.preventDefault();yaw+=(e.key==="ArrowLeft"?-.15:.15);}};
  const visibility=()=>{last=0;};
  const hide=()=>dispose();
  function dispose(){
    if(disposed)return;disposed=true;cancelAnimationFrame(frame);
    canvas.removeEventListener("webglcontextlost",onContextLoss);
    canvas.removeEventListener("pointerdown",pointerDown);
    canvas.removeEventListener("pointermove",pointerMove);
    canvas.removeEventListener("pointerup",pointerUp);
    canvas.removeEventListener("pointercancel",pointerUp);
    canvas.removeEventListener("keydown",key);
    window.removeEventListener("pagehide",hide);
    document.removeEventListener("visibilitychange",visibility);
    if(gl){if(buffer)gl.deleteBuffer(buffer);if(normalBuffer)gl.deleteBuffer(normalBuffer);
      if(colorBuffer)gl.deleteBuffer(colorBuffer);if(indexBuffer)gl.deleteBuffer(indexBuffer);
      if(program)gl.deleteProgram(program);}
  }
  try{
    const mesh=createAvatarGeometry();
    const vs=compile(gl,gl.VERTEX_SHADER,VERTEX),fs=compile(gl,gl.FRAGMENT_SHADER,FRAGMENT);
    program=gl.createProgram();if(!program)throw Error("PROGRAM_ALLOC");
    gl.attachShader(program,vs);gl.attachShader(program,fs);gl.linkProgram(program);
    gl.deleteShader(vs);gl.deleteShader(fs);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error("PROGRAM_LINK");
    const attributes=[[0,mesh.positions],[1,mesh.normals],[2,mesh.colors]];
    for(const [location,data] of attributes){
      const b=gl.createBuffer();if(!b)throw Error("VERTEX_ALLOC");
      if(location===0)buffer=b;else if(location===1)normalBuffer=b;else colorBuffer=b;
      gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);
      gl.enableVertexAttribArray(location);gl.vertexAttribPointer(location,3,gl.FLOAT,false,0,0);
    }
    indexBuffer=gl.createBuffer();if(!indexBuffer)throw Error("INDEX_ALLOC");
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,mesh.indices,gl.STATIC_DRAW);
    gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);
    gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
    const projection=gl.getUniformLocation(program,"uProjection"),uYaw=gl.getUniformLocation(program,"uYaw"),uBreath=gl.getUniformLocation(program,"uBreath");
    const reduced=window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches??false;
    function render(time){
      if(disposed)return;
      frame=requestAnimationFrame(render);
      if(document.hidden||(!reduced&&time-last<50))return;
      last=time;
      const rect=canvas.getBoundingClientRect(),w=Math.max(1,Math.min(1600,Math.round(rect.width*Math.min(1.5,window.devicePixelRatio||1)))),
        h=Math.max(1,Math.min(1600,Math.round(rect.height*Math.min(1.5,window.devicePixelRatio||1))));
      if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h);}
      const f=1/Math.tan(.78/2),aspect=w/h,near=.1,far=100;
      const m=new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)/(near-far),-1,0,0,2*far*near/(near-far),0]);
      gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
      gl.useProgram(program);gl.uniformMatrix4fv(projection,false,m);
      gl.uniform1f(uYaw,yaw+(reduced?0:.07*Math.sin(time/2300)));
      gl.uniform1f(uBreath,reduced?0:Math.sin(time/1300));
      // Explicitly rebind attributes in case the WebGL context altered VAO state.
      for(const [loc,b] of [[0,buffer],[1,normalBuffer],[2,colorBuffer]]){
        gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.vertexAttribPointer(loc,3,gl.FLOAT,false,0,0);
      }
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);
      gl.drawElements(gl.TRIANGLES,mesh.indices.length,gl.UNSIGNED_INT,0);
    }
    canvas.addEventListener("webglcontextlost",onContextLoss,false);
    canvas.addEventListener("pointerdown",pointerDown);
    canvas.addEventListener("pointermove",pointerMove);
    canvas.addEventListener("pointerup",pointerUp);
    canvas.addEventListener("pointercancel",pointerUp);
    canvas.addEventListener("keydown",key);
    document.addEventListener("visibilitychange",visibility);
    window.addEventListener("pagehide",hide,{once:true});
    if(fallback)fallback.hidden=true;canvas.hidden=false;
    if(report)report.textContent="LIVE PROCEDURAL 3D · DRAG TO ROTATE · RIG PENDING";
    frame=requestAnimationFrame(render);
    return {status:"WEBGL2_SOURCE_RUNTIME_CANDIDATE",triangles:mesh.triangles,dispose};
  }catch{
    dispose();canvas.hidden=true;if(fallback)fallback.hidden=false;
    if(report)report.textContent="3D initialization unavailable · 2D fallback";
    return {status:"FALLBACK",dispose(){}};
  }
}
