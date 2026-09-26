(function($){
  'use strict';
  const $cockpit=$('#luhmCockpit');
  $cockpit.luhmDeck();
  $cockpit.luhmSite({home:'cathedral'});
  $cockpit.on('luhm:site:route',function(_e,payload){
    $('[data-site-status]').text('Site '+String(payload.route||'unknown'));
  });
  $(document).on('luhm:bridge:preview',function(_e,msg){
    if(msg.type==='status.request'){
      $('[data-kai-status]').text('KAI 9000 · preview');
      $('[data-ollama-status]').text('Ollama · unprobed');
    }
  });
  window.addEventListener('message',function(event){
    let msg=event.data;
    try{if(typeof msg==='string')msg=JSON.parse(msg)}catch{return}
    if(!msg||msg.schema!=='luhm.bridge.reply.v1')return;
    if(msg.type==='status'){
      $('[data-kai-status]').text('KAI '+String(msg.payload?.kai||'unknown'));
      $('[data-ollama-status]').text('Ollama '+String(msg.payload?.ollama||'unknown'));
    }
  });
})(jQuery);
