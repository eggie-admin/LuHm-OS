(function($){
  'use strict';

  const defaults={
    channel:'KAI 9000 Proposed',
    drivePath:'LuHm OS / builds / KAI9000 / proposed / 2026-09-26',
    sourceStatus:'candidate',
    ciStatus:'pending',
    driveStatus:'pending',
    deviceStatus:'human install required'
  };

  $.fn.luhmDelivery=function(options){
    const settings=$.extend({},defaults,options||{});
    return this.each(function(){
      const $root=$(this);
      function paint(){
        $root.find('[data-delivery-channel]').text(settings.channel);
        $root.find('[data-delivery-source]').text(settings.sourceStatus);
        $root.find('[data-delivery-ci]').text(settings.ciStatus);
        $root.find('[data-delivery-drive]').text(settings.driveStatus);
        $root.find('[data-delivery-drive-path]').text(settings.drivePath);
        $root.find('[data-delivery-device]').text(settings.deviceStatus);
      }
      $root.data('luhmDeliverySet',function(update){
        $.extend(settings,update||{});
        paint();
      });
      paint();
    });
  };
})(jQuery);
