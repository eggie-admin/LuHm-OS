(function($){
  'use strict';
  const $cockpit=$('#luhmCockpit');
  $cockpit.luhmDeck();
  $cockpit.luhmSite({home:'cathedral'});
  $('[data-delivery-widget]').luhmDelivery({
    channel:'KAI 9000 Proposed · 1.0.23',
    drivePath:'LuHm OS / builds / KAI9000 / proposed / 2026-09-26',
    sourceStatus:'exact-head candidate',
    ciStatus:'device-independent build receipt required',
    driveStatus:'connector receipt required',
    deviceStatus:'Professor install + smoke required'
  });

  function packageVersion(system,name){
    const item=system?.packages?.[name];
    return item&&item.versionName?String(item.versionName):'not installed';
  }

  function shizukuText(system){
    const item=system?.shizuku||{};
    if(!item.binderAlive)return 'unavailable';
    const identity=String(item.identity||'unknown');
    const permission=String(item.permission||'unknown');
    return identity+' · '+permission;
  }

  function setDelivery(update){
    const setter=$('[data-delivery-widget]').data('luhmDeliverySet');
    if(typeof setter==='function')setter(update);
  }

  function handleReply(data){
    let msg=data;
    try{if(typeof msg==='string')msg=JSON.parse(msg)}catch{return}
    if(!msg||msg.schema!=='luhm.bridge.reply.v1')return;
    if(msg.type==='status'){
      $('[data-kai-status]').text('KAI '+String(msg.payload?.kai||'unknown'));
      $('[data-ollama-status]').text('Ollama '+String(msg.payload?.ollama||'unknown'));
      const system=msg.payload?.system||{};
      const provider=system.webViewProvider||{};
      const providerText=provider.packageName
        ? String(provider.packageName)+' '+String(provider.versionName||'')
        : 'WebView unavailable';
      const deviceText=[system.model||'Android',system.sdk?'SDK '+system.sdk:''].filter(Boolean).join(' · ');
      const adminText=String(system.adminMode||'standard_app');
      const shizuku=shizukuText(system);
      $('[data-device-status]').text(deviceText);
      $('[data-webview-status]').text(providerText);
      $('[data-admin-status]').text(adminText);
      $('[data-shizuku-status]').text('Shizuku '+shizuku);
      $('[data-system-device]').text(deviceText+' · Android '+String(system.androidRelease||'?'));
      $('[data-system-webview]').text(providerText);
      $('[data-system-chrome]').text(packageVersion(system,'com.chrome.canary'));
      $('[data-system-profile]').text(system.managedProfile?'managed/profile-isolated':'primary/standard');
      $('[data-system-admin]').text(adminText);
      $('[data-system-shizuku]').text(shizuku+' · native explicit grant only');
      setDelivery({deviceStatus:'device probe received · install smoke still human-gated'});
      return;
    }
    if(msg.type==='delivery.status'){
      const payload=msg.payload||{};
      setDelivery({
        sourceStatus:String(payload.source||'candidate'),
        ciStatus:String(payload.ci||'unknown'),
        driveStatus:String(payload.drive||'unknown'),
        deviceStatus:String(payload.device||'human install required')
      });
      $('[data-delivery-badge]').text('Delivery '+String(payload.ci||'candidate'));
      return;
    }
    if(msg.type==='chat.reply'){
      const speaker=String(msg.payload?.speaker||'Lum');
      const text=String(msg.payload?.message||'');
      $('<p>').append($('<b>').text(speaker+': '),document.createTextNode(text))
        .appendTo('[data-message-stream]');
    }
  }

  $cockpit.on('luhm:site:route',function(_e,payload){
    $('[data-site-status]').text('Site '+String(payload.route||'unknown'));
  });

  $(document).on('luhm:bridge:preview',function(_e,msg){
    if(msg.type==='status.request'){
      $('[data-kai-status]').text('KAI 9000 · preview');
      $('[data-ollama-status]').text('Ollama · unprobed');
      $('[data-webview-status]').text('WebView · device probe required');
      $('[data-admin-status]').text('Admin · device probe required');
      $('[data-shizuku-status]').text('Shizuku · device probe required');
    }
  });

  if(window.LuHmNative&&typeof window.LuHmNative.postMessage==='function'){
    window.LuHmNative.onmessage=function(event){handleReply(event.data)};
  }
  window.addEventListener('message',function(event){handleReply(event.data)});
})(jQuery);
