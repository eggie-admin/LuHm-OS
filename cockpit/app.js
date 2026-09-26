(function($){
  'use strict';
  const $cockpit=$('#luhmCockpit');
  $cockpit.luhmDeck();
  $cockpit.luhmSite({home:'cathedral'});
  $('[data-delivery-widget]').luhmDelivery({
    channel:'KAI 9000 Kiosk · 1.0.24',
    drivePath:'LuHm OS / builds / KAI9000 / proposed / 2026-09-26',
    sourceStatus:'exact-head candidate',
    ciStatus:'build receipt required',
    driveStatus:'connector receipt required',
    deviceStatus:'Professor install + smoke required'
  });

  function setMode(mode){
    if(!['full','mini','pet','bubble'].includes(mode))return;
    document.documentElement.setAttribute('data-shell-mode',mode);
  }
  function packageVersion(system,name){const item=system?.packages?.[name];return item&&item.versionName?String(item.versionName):'not installed'}
  function shizukuText(system){const item=system?.shizuku||{};if(!item.binderAlive)return'unavailable';return String(item.identity||'unknown')+' · '+String(item.permission||'unknown')}
  function setDelivery(update){const setter=$('[data-delivery-widget]').data('luhmDeliverySet');if(typeof setter==='function')setter(update)}

  function handleReply(data){
    let msg=data;try{if(typeof msg==='string')msg=JSON.parse(msg)}catch{return}
    if(!msg||msg.schema!=='luhm.bridge.reply.v1')return;
    if(msg.type==='status'){
      const system=msg.payload?.system||{};
      const provider=system.webViewProvider||{};
      const providerText=provider.packageName?String(provider.packageName)+' '+String(provider.versionName||''):'WebView unavailable';
      const chromeCanary=packageVersion(system,'com.chrome.canary');
      const webviewCanary=packageVersion(system,'com.google.android.webview.canary');
      const deviceText=[system.model||'Android',system.sdk?'SDK '+system.sdk:''].filter(Boolean).join(' · ');
      const adminText=String(system.adminMode||'standard_app');
      const shizuku=shizukuText(system);
      $('[data-kai-status]').text('KAI '+String(msg.payload?.kai||'unknown'));
      $('[data-ollama-status]').text('Ollama '+String(msg.payload?.ollama||'unknown'));
      $('[data-webview-status]').text(providerText);
      $('[data-shizuku-status]').text('Shizuku '+shizuku);
      $('[data-system-device]').text(deviceText+' · Android '+String(system.androidRelease||'?'));
      $('[data-system-webview]').text(providerText+' · Canary installed '+webviewCanary);
      $('[data-system-chrome]').text(chromeCanary);
      $('[data-system-profile]').text(system.managedProfile?'managed/profile-isolated':'primary/standard');
      $('[data-system-admin]').text(adminText);
      $('[data-system-shizuku]').text(shizuku+' · native explicit grant only');
      $('[data-pet-webview]').text(provider.packageName?.includes('canary')?'CANARY':'SYSTEM');
      $('[data-mini-state]').text(provider.packageName?.includes('canary')?'WEBVIEW CANARY':'SYSTEM WEBVIEW');
      if(msg.payload?.cockpitMode)setMode(String(msg.payload.cockpitMode));
      setDelivery({deviceStatus:'device probe received · physical smoke still human-gated'});
      return;
    }
    if(msg.type==='delivery.status'){
      const payload=msg.payload||{};
      setDelivery({sourceStatus:String(payload.source||'candidate'),ciStatus:String(payload.ci||'unknown'),driveStatus:String(payload.drive||'unknown'),deviceStatus:String(payload.device||'human install required')});
      return;
    }
    if(msg.type==='chat.reply'){
      const speaker=String(msg.payload?.speaker||'Lum');const text=String(msg.payload?.message||'');
      $('<p>').append($('<b>').text(speaker+': '),document.createTextNode(text)).appendTo('[data-message-stream]');
    }
  }

  $(document).on('luhm:bridge:preview',function(_e,msg){
    if(msg.type==='ui.mode')setMode(String(msg.payload?.mode||''));
    if(msg.type==='status.request'){
      $('[data-kai-status]').text('KAI preview');
      $('[data-webview-status]').text('device probe required');
      $('[data-shizuku-status]').text('Shizuku device probe required');
    }
  });
  if(window.LuHmNative&&typeof window.LuHmNative.postMessage==='function')window.LuHmNative.onmessage=function(event){handleReply(event.data)};
  window.addEventListener('message',function(event){handleReply(event.data)});
})(jQuery);
