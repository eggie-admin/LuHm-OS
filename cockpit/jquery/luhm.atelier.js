(function($){
  'use strict';

  const sliders=[
    ['height','HEIGHT'],
    ['head','HEAD'],
    ['shoulders','SHOULDERS'],
    ['torso','TORSO'],
    ['arms','ARMS'],
    ['legs','LEGS'],
    ['hips','HIPS'],
    ['frame','FRAME']
  ];
  const presets={
    default:{height:50,head:50,shoulders:50,torso:50,arms:50,legs:50,hips:50,frame:50},
    tallOni:{height:78,head:44,shoulders:68,torso:63,arms:61,legs:76,hips:54,frame:58},
    pocketOni:{height:24,head:72,shoulders:44,torso:38,arms:40,legs:31,hips:58,frame:46},
    heroic:{height:58,head:46,shoulders:76,torso:57,arms:64,legs:58,hips:60,frame:72}
  };

  const queued={};
  let frame=0;

  function send(type,payload){
    if(window.LuHmBridge)window.LuHmBridge.send(type,payload||{});
  }

  function queueTune(key,value){
    queued[key]=Math.max(0,Math.min(100,Number(value)||0))/100;
    if(frame)return;
    frame=requestAnimationFrame(function(){
      frame=0;
      Object.keys(queued).forEach(function(name){
        send('avatar.tune',{key:name,value:queued[name]});
        delete queued[name];
      });
    });
  }

  function setSlider($slider,value,notify){
    const v=Math.max(0,Math.min(100,Math.round(value)));
    $slider.slider('value',v);
    $slider.closest('.atelierRow').find('[data-slider-value]').text(String(v).padStart(2,'0'));
    if(notify!==false)queueTune(String($slider.data('body-slider')),v);
  }

  function applyPreset(name){
    const preset=presets[name];
    if(!preset)return;
    $('[data-body-slider]').each(function(){
      const $s=$(this),key=String($s.data('body-slider'));
      setSlider($s,preset[key]??50,true);
    });
  }

  $.fn.luhmAtelier=function(){
    return this.each(function(){
      const $root=$(this);
      const $rows=$root.find('[data-atelier-sliders]').empty();

      sliders.forEach(function(spec){
        const key=spec[0],label=spec[1];
        const $row=$('<div class="atelierRow">');
        const $top=$('<div class="atelierLabel">')
          .append($('<span>').text(label))
          .append($('<b data-slider-value>').text('50'));
        const $slider=$('<div class="atelierSlider">').attr('data-body-slider',key).data('body-slider',key);
        $row.append($top,$slider).appendTo($rows);
        $slider.slider({
          min:0,max:100,value:50,step:1,
          slide:function(_event,ui){
            $row.find('[data-slider-value]').text(String(ui.value).padStart(2,'0'));
            queueTune(key,ui.value);
          },
          change:function(_event,ui){
            $row.find('[data-slider-value]').text(String(ui.value).padStart(2,'0'));
          }
        });
      });

      $root.on('click','[data-atelier-preset]',function(){
        applyPreset(String($(this).attr('data-atelier-preset')||'default'));
      });

      $root.on('click','[data-atelier-random]',function(){
        $('[data-body-slider]').each(function(){
          setSlider($(this),20+Math.floor(Math.random()*61),true);
        });
      });

      $root.on('click','[data-atelier-reset]',function(){
        $('[data-body-slider]').each(function(){setSlider($(this),50,false)});
        send('avatar.reset',{});
      });

      $root.on('click','[data-avatar-inspect]',function(){
        send('avatar.inspect',{});
      });

      $(document).on('luhm:bridge:reply',function(_event,msg){
        if(!msg||msg.type!=='avatar.summary')return;
        const p=msg.payload||{};
        const morphs=Number(p.mesh_morph_targets||0);
        const bones=Number(p.skeleton_bones||0);
        const mapped=Number(p.canonical_mapped||0);
        const required=Number(p.canonical_required||0);
        $root.find('[data-atelier-capability]').text(
          'RIG '+mapped+'/'+required+' · BONES '+bones+' · MORPHS '+morphs
        );
      });
    });
  };

  $(function(){
    $('#luhmCockpit').luhmAtelier();
    setTimeout(function(){send('avatar.inspect',{})},320);
  });
})(jQuery);
