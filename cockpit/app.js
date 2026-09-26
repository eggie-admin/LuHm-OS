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
      $('[data-kai-status]').text('KAI '+String(msg.payload?.kai||'unknown'));
      $('[data-ollama-status]').text('Ollama '+String(msg.payload?.ollama||'unknown'));
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
    }
  });

  if(window.LuHmNative&&typeof window.LuHmNative.postMessage==='function'){
    window.LuHmNative.onmessage=function(event){handleReply(event.data)};
  }
  window.addEventListener('message',function(event){handleReply(event.data)});
})(jQuery);
