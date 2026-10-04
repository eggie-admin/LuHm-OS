(function($){
  'use strict';
  const $cockpit=$('#luhmCockpit');
  $cockpit.luhmDeck();
  $cockpit.luhmSite({home:'cathedral'});

  function packageVersion(system,name){
    const item=system?.packages?.[name];
    return item&&item.versionName?String(item.versionName):'not installed';
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
      $('[data-device-status]').text(deviceText);
      $('[data-webview-status]').text(providerText);
      $('[data-admin-status]').text(adminText);
      $('[data-system-device]').text(deviceText+' · Android '+String(system.androidRelease||'?'));
      $('[data-system-webview]').text(providerText);
      $('[data-system-chrome]').text(packageVersion(system,'com.chrome.canary'));
      $('[data-system-profile]').text(system.managedProfile?'managed/profile-isolated':'primary/standard');
      $('[data-system-admin]').text(adminText);
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
    }
  });

  if(window.LuHmNative&&typeof window.LuHmNative.postMessage==='function'){
    window.LuHmNative.onmessage=function(event){handleReply(event.data)};
  }
  window.addEventListener('message',function(event){handleReply(event.data)});
})(jQuery);
