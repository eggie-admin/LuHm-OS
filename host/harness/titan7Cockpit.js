/* Titan 7: locally pinned jQuery UI with no provider-authority side effects. */
(function($){
"use strict";
if(!$ || !$.fn || typeof $.fn.accordion!=="function")throw new Error("locally pinned jQuery UI required");
var modes=Object.freeze({default:"normal ChatGPT",ic:"in-character scene",ooc:"out-of-character project",irl:"real-life context"});
$.fn.luhmTitan7=function(){
 return this.each(function(){
  var root=$(this);
  if(root.data("luhmTitan7"))return;
  root.data("luhmTitan7",{mode:"default"});
  root.find("#titan7Accordion").accordion({header:"h3",collapsible:true,active:false,heightStyle:"content",animate:false});
  root.on("click.luhmTitan7","[data-luhm-mode]",function(){
   var mode=String($(this).attr("data-luhm-mode")||"");
   if(!Object.prototype.hasOwnProperty.call(modes,mode))return;
   root.find("[data-luhm-mode]").attr("aria-pressed","false");
   $(this).attr("aria-pressed","true");
   root.data("luhmTitan7").mode=mode;
   root.find("#titanModeState").text(mode.toUpperCase()+" · "+modes[mode]+". UI only; ChatGPT host and workers unchanged.");
   root.trigger("luhm:conversation:mode",[{mode:mode,authorityEffect:"none",workerExecution:"QUARANTINED",hostSync:"UNVERIFIED"}]);
  });
 });
};
$(function(){$("[data-luhm-titan7]").luhmTitan7();});
}(window.jQuery));
