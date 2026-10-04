(function($){
  'use strict';
  const $cockpit=$('#luhmCockpit');
  $cockpit.luhmDeck();
  $cockpit.luhmSite({home:'cathedral'});

  function handleReply(data){
    let msg=data;
    try{if(typeof msg==='string')msg=JSON.parse(msg)}catch{return}
    if(!msg||msg.schema!=='luhm.bridge.reply.v1')return;
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
  });
  if(window.LuHmNative&&typeof window.LuHmNative.postMessage==='function'){
    window.LuHmNative.onmessage=function(event){handleReply(event.data)};
  }
  window.addEventListener('message',function(event){handleReply(event.data)});
  setTimeout(()=>window.LuHmBridge&&window.LuHmBridge.send('status.request',{}),180);
})(jQuery);
