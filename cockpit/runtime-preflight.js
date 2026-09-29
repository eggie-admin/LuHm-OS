(function(window, document){
  'use strict';

  const jq=window.jQuery;
  const checks={
    jquery:!!(jq&&jq.fn),
    sameGlobal:!!(jq&&window.$===jq),
    widgetFactory:!!(jq&&typeof jq.widget==='function'),
    draggable:!!(jq&&jq.fn&&typeof jq.fn.draggable==='function'),
    resizable:!!(jq&&jq.fn&&typeof jq.fn.resizable==='function'),
    slider:!!(jq&&jq.fn&&typeof jq.fn.slider==='function')
  };
  const missing=Object.keys(checks).filter(function(key){return !checks[key]});
  const state=Object.freeze({
    schema:'luhm.webglass.preflight.v1',
    status:missing.length?'RED':'GREEN',
    checks:checks,
    missing:missing.slice()
  });
  window.__LUHM_WEBGLASS_PREFLIGHT__=state;
  window.LuHmBootBlocked=missing.length>0;

  if(!missing.length)return;

  const message='LuHm WebGlass dependency preflight failed: '+missing.join(', ');
  console.error(message,state);

  function renderFailure(){
    document.documentElement.setAttribute('data-luhm-boot','red');
    if(!document.body)return;
    document.body.innerHTML='';
    const main=document.createElement('main');
    main.style.cssText='min-height:100vh;padding:24px;background:#030914;color:#f4f7ff;font:16px/1.45 system-ui,sans-serif';
    const title=document.createElement('h1');
    title.textContent='LUHM WEBGLASS BOOT BLOCKED';
    const note=document.createElement('p');
    note.textContent='The packaged cockpit stopped before plugin initialization so a broken UI cannot masquerade as GREEN.';
    const pre=document.createElement('pre');
    pre.style.cssText='white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;border:1px solid #33456c;border-radius:8px;background:#081222';
    pre.textContent=message;
    main.append(title,note,pre);
    document.body.appendChild(main);
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',renderFailure,{once:true});
  else renderFailure();
})(window,document);
