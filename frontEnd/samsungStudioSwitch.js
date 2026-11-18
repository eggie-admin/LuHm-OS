/* LuHm-OS on-device studio route. Presentation only; no external shell bridge. */
(() => {
  "use strict";
  const ready = () => {
    const root = document.querySelector("[data-luhm-cockpit]");
    const panel = root?.querySelector("[data-luhm-studio-bridge]");
    if (!root || !panel) return;
    const feedback = panel.querySelector("[data-luhm-studio-status]");
    const open = () => {
      const otherPanels = ["[data-luhm-menu]", "[data-luhm-asset-factory]", "[data-luhm-system-layer]"];
      otherPanels.forEach(selector => {const item=root.querySelector(selector); if(item)item.hidden=true;});
      panel.hidden=false;
      panel.querySelector("[data-luhm-studio-close]")?.focus();
      feedback.textContent="Select a workstation role. No remote command is executed.";
    };
    const close = () => {
      panel.hidden=true;
      root.querySelector("[data-luhm-studio-open]")?.focus();
    };
    const select = (role) => {
      if (!["samsungCore","blenderGarage"].includes(role)) return;
      panel.querySelectorAll("[data-luhm-studio-mode]").forEach(button=>{
        const active=button.dataset.luhmStudioMode===role;
        button.setAttribute("aria-pressed",String(active));
      });
      panel.querySelectorAll("[data-luhm-studio-detail]").forEach(item=>{
        item.hidden=item.dataset.luhmStudioDetail!==role;
      });
      feedback.textContent=role==="samsungCore"
        ?"Samsung Core selected: local WebView/Godot interface, no privileged shell."
        :"Blender Studio selected: remote Linux workflow description, not live connectivity.";
    };
    root.querySelectorAll("[data-luhm-studio-open]").forEach(button=>button.addEventListener("click",open));
    panel.querySelector("[data-luhm-studio-close]")?.addEventListener("click",close);
    panel.querySelectorAll("[data-luhm-studio-mode]").forEach(button=>
      button.addEventListener("click",()=>select(button.dataset.luhmStudioMode)));
    panel.addEventListener("keydown",event=>{if(event.key==="Escape")close();});
    select("samsungCore");
  };
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",ready,{once:true});
  else ready();
})();
