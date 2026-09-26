(function($){
  'use strict';

  const rituals={
    crown_wake:{title:'I · CROWN WAKE',note:'Neon crown pulse + Lum wake'},
    oni_trinity:{title:'II · ONI TRINITY',note:'Three oni lights + Crown echo'},
    witching_hour:{title:'III · WITCHING HOUR',note:'Full toy sequence · no backend mutation'}
  };

  function send(id){
    if(!rituals[id]||!window.LuHmBridge)return;
    $('[data-ritual-state]').text('REQUESTED · '+rituals[id].title);
    $('[data-ritual-start]').prop('disabled',true);
    window.LuHmBridge.send('ritual.start',{ritual:id});
  }

  $.fn.luhmRituals=function(){
    return this.each(function(){
      const $root=$(this);
      $root.on('click','[data-ritual-start]',function(){
        send(String($(this).attr('data-ritual-start')||''));
      });

      $(document).on('luhm:bridge:reply',function(_event,msg){
        if(!msg||msg.type!=='ritual.status')return;
        const p=msg.payload||{};
        const id=String(p.ritual||'none');
        const state=String(p.state||'unknown').toUpperCase();
        const title=rituals[id]?.title||id.toUpperCase();
        $('[data-ritual-state]').text(state+' · '+title);
        $('[data-ritual-start]').prop('disabled',Boolean(p.busy));
      });
    });
  };

  $(function(){
    $('#luhmCockpit').luhmRituals();
  });
})(jQuery);
