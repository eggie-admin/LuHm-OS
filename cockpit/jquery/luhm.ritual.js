(function($){
  'use strict';

  const rituals={
    crown_wake:{title:'I · CROWN WAKE',note:'Neon crown pulse + Lum wake'},
    oni_trinity:{title:'II · ONI TRINITY',note:'Three oni lights + Crown echo'},
    witching_hour:{title:'III · WITCHING HOUR',note:'Full toy sequence · reversible · no backend mutation'}
  };

  let busy=false;
  let doctrineValid=false;
  let allowed=new Set();

  function refresh(){
    $('[data-ritual-start]').each(function(){
      const id=String($(this).attr('data-ritual-start')||'');
      $(this).prop('disabled',busy||!doctrineValid||!allowed.has(id));
    });
  }

  function requestCapabilities(){
    if(!window.LuHmBridge)return;
    window.LuHmBridge.send('system.capabilities',{});
  }

  function send(id){
    if(!window.LuHmBridge||busy||!doctrineValid||!allowed.has(id)||!rituals[id])return;
    $('[data-ritual-state]').text('REQUESTED · '+rituals[id].title);
    busy=true;
    refresh();
    window.LuHmBridge.send('ritual.start',{ritual:id});
  }

  $.fn.luhmRituals=function(){
    return this.each(function(){
      const $root=$(this);
      refresh();

      $root.on('click','[data-ritual-start]',function(){
        send(String($(this).attr('data-ritual-start')||''));
      });

      $(document).on('luhm:bridge:reply',function(_event,msg){
        if(!msg)return;

        if(msg.type==='system.capabilities'){
          const p=msg.payload||{};
          doctrineValid=Boolean(p.valid);
          const caps=p.capabilities||{};
          const ids=Array.isArray(caps.rituals)?caps.rituals:[];
          allowed=new Set(ids.filter(id=>Object.prototype.hasOwnProperty.call(rituals,id)));
          $('[data-ritual-state]').text(doctrineValid?'DOCTRINE · ARMED':'DOCTRINE · BLOCKED');
          refresh();
          return;
        }

        if(msg.type==='bridge.rejected'){
          const p=msg.payload||{};
          busy=false;
          $('[data-ritual-state]').text('BLOCKED · '+String(p.reason||'doctrine'));
          refresh();
          return;
        }

        if(msg.type!=='ritual.status')return;
        const p=msg.payload||{};
        const id=String(p.ritual||'none');
        const state=String(p.state||'unknown').toUpperCase();
        const title=rituals[id]?.title||id.toUpperCase();
        busy=Boolean(p.busy);
        doctrineValid=Boolean(p.doctrine_valid!==false);
        if(Array.isArray(p.allowed))allowed=new Set(p.allowed);
        $('[data-ritual-state]').text(state+' · '+title);
        refresh();
      });

      requestCapabilities();
    });
  };

  $(function(){
    $('#luhmCockpit').luhmRituals();
  });
})(jQuery);
