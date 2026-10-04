(function($){
  'use strict';
  const NS='luhmDeck';
  const allowed=new Set(['chat.send','panel.set','status.request','model.select','cms.select','world.show','toy.action','input.axis','camera.delta','window.mode','app.background','app.quit','avatar.tune','avatar.reset','avatar.inspect']);
  const modes=new Set(['bubble','compact','panel','fullscreen','hidden']);

  function nativeSend(type,payload){
    if(!allowed.has(type))throw new Error('bridge message not allowlisted: '+type);
    const message=JSON.stringify({schema:'luhm.bridge.v1',type,payload:payload||{},ts:Date.now()});
    if(window.LuHmNative&&typeof window.LuHmNative.postMessage==='function'){
      window.LuHmNative.postMessage(message);return true;
    }
    $(document).trigger('luhm:bridge:preview',[JSON.parse(message)]);return false;
  }

  function setMode(mode,notify){
    if(!modes.has(mode))return;
    document.body.dataset.mode=mode;
    if(notify!==false)nativeSend('window.mode',{mode});
  }
  window.LuHmUISetMode=function(mode){setMode(String(mode||''),false)};

  $.fn[NS]=function(){return this.each(function(){
    const $root=$(this);
    $root.find('[data-luhm-panel]').each(function(){
      $(this).draggable({handle:'.panelTitle',containment:'window',scroll:false})
        .resizable({handles:'se',minWidth:230,minHeight:120});
    });
    $root.on('click','[data-toggle-panel]',function(){
      const id=$(this).attr('data-toggle-panel');
      $('#'+id).toggle().css('z-index',100+Date.now()%1000);
    });
    $(document).on('click','[data-window-mode]',function(){setMode(String($(this).attr('data-window-mode')||''),true)});
    $root.on('submit','[data-chat-form]',function(e){
      e.preventDefault();const input=this.elements.message;const text=String(input.value||'').trim();if(!text)return;
      nativeSend('chat.send',{message:text});
      $root.find('[data-message-stream]').append($('<p>').text('Professor: '+text));input.value='';
    });
    $root.on('click','[data-request-status]',()=>nativeSend('status.request',{}));
    $root.on('click','[data-native-world]',()=>{nativeSend('world.show',{});setMode('compact',true)});
    $root.on('click','[data-toy-action]',function(){nativeSend('toy.action',{action:String($(this).attr('data-toy-action')||'')})});
    $root.on('click','[data-app-background]',()=>nativeSend('app.background',{}));
    $root.on('click','[data-app-quit]',()=>nativeSend('app.quit',{}));
    $root.on('luhm:model:select',(e,id)=>nativeSend('model.select',{modelId:String(id)}));
    $root.on('luhm:cms:select',(e,id)=>nativeSend('cms.select',{entryId:String(id)}));

    const stopAxis=()=>nativeSend('input.axis',{x:0,y:0});
    $root.on('pointerdown','[data-axis]',function(e){
      e.preventDefault();this.setPointerCapture&&this.setPointerCapture(e.pointerId);
      const parts=String($(this).attr('data-axis')).split(',').map(Number);
      nativeSend('input.axis',{x:parts[0]||0,y:parts[1]||0});
    });
    $root.on('pointerup pointercancel pointerleave','[data-axis]',stopAxis);
    window.addEventListener('blur',stopAxis);

    let cameraPointer=null,lastX=0,lastY=0;
    $root.on('pointerdown','[data-camera-pad]',function(e){
      cameraPointer=e.pointerId;lastX=e.clientX;lastY=e.clientY;this.setPointerCapture&&this.setPointerCapture(e.pointerId);e.preventDefault();
    });
    $root.on('pointermove','[data-camera-pad]',function(e){
      if(cameraPointer!==e.pointerId)return;
      const dx=e.clientX-lastX,dy=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;
      if(dx||dy)nativeSend('camera.delta',{dx,dy});e.preventDefault();
    });
    $root.on('pointerup pointercancel','[data-camera-pad]',function(e){if(cameraPointer===e.pointerId)cameraPointer=null});
  })};
  window.LuHmBridge={send:nativeSend,allowed:[...allowed],setMode};
})(jQuery);
