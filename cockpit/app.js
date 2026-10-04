(function($){
  'use strict';

  function renderBootFailure(message){
    window.LuHmBootBlocked=true;
    console.error('LuHm WebGlass boot blocked',message);
    const render=function(){
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
    };
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',render,{once:true});
    else render();
  }

  const checks={
    jquery:!!($&&$.fn),
    sameGlobal:!!($&&window.$===$),
    widgetFactory:!!($&&typeof $.widget==='function'),
    draggable:!!($&&$.fn&&typeof $.fn.draggable==='function'),
    resizable:!!($&&$.fn&&typeof $.fn.resizable==='function'),
    slider:!!($&&$.fn&&typeof $.fn.slider==='function')
  };
  const missing=Object.keys(checks).filter(function(key){return !checks[key]});
  window.__LUHM_WEBGLASS_PREFLIGHT__=Object.freeze({
    schema:'luhm.webglass.preflight.v1',
    status:missing.length?'RED':'GREEN',
    checks:checks,
    missing:missing.slice()
  });
  if(missing.length){
    renderBootFailure('dependency preflight failed: '+missing.join(', '));
    return;
  }
  window.LuHmBootBlocked=false;
  document.documentElement.setAttribute('data-luhm-boot','green');

  const $cockpit=$('#luhmCockpit');
  $cockpit.luhmDeck();
  $cockpit.luhmSite({home:'cathedral'});

  function handleReply(data){
    let msg=data;
    try{if(typeof msg==='string')msg=JSON.parse(msg)}catch{return}
    if(!msg||msg.schema!=='luhm.bridge.reply.v1')return;
    $(document).trigger('luhm:bridge:reply',[msg]);
    if(msg.type==='status'){
      const p=msg.payload||{};
      $('[data-webview-status]').text(String(p.webviewPackage||'unknown').replace('com.google.android.webview.','wv:')+' '+String(p.webviewVersion||''));
      $('[data-site-status]').text(String(p.mode||document.body.dataset.mode||'glass').toUpperCase());
      return;
    }
    if(msg.type==='chat.reply'){
      const speaker=String(msg.payload?.speaker||'Lum');
      const text=String(msg.payload?.message||'');
      $('<p>').append($('<b>').text(speaker+': '),document.createTextNode(text)).appendTo('[data-message-stream]');
    }
  }

  $cockpit.on('luhm:site:route',function(_e,payload){
    $('[data-site-status]').text(String(payload.route||'unknown').toUpperCase());
  });
  $(document).on('luhm:bridge:preview',function(_e,msg){
    if(msg.type==='status.request')$('[data-webview-status]').text('desktop preview');
    if(msg.type==='avatar.inspect'){
      $(document).trigger('luhm:bridge:reply',[{
        schema:'luhm.bridge.reply.v1',
        type:'avatar.summary',
        payload:{mode:'desktop_preview',mesh_morph_targets:0,skeleton_bones:0,canonical_mapped:0,canonical_required:22}
      }]);
    }
  });
  if(window.LuHmNative&&typeof window.LuHmNative.postMessage==='function'){
    window.LuHmNative.onmessage=function(event){handleReply(event.data)};
  }
  window.addEventListener('message',function(event){handleReply(event.data)});
  setTimeout(()=>window.LuHmBridge&&window.LuHmBridge.send('status.request',{}),180);
})(window.jQuery);
