import {orderedActions,initialCounts,sortActions,selectAction} from "../src/workflow-rank.mjs";
const details={
 play:{label:"Play First Night",hint:"Playable game proof exists in the separate First Night draft.",source:"https://github.com/eggie-admin/LuHm-OS/pull/475",link:"Review game draft"},
 edit:{label:"Edit Scene",hint:"Scene editor belongs to the First Night browser prototype.",source:"https://github.com/eggie-admin/LuHm-OS/pull/475",link:"Review editor draft"},
 assets:{label:"Review Assets",hint:"Check rights and approved art before importing.",source:"https://github.com/eggie-admin/LuHm-OS/tree/main/artAssets",link:"Inspect art inventory"},
 build:{label:"Build & Test",hint:"Inspect exact-source GitHub CI and the Debian backend.",source:"https://github.com/eggie-admin/LuHm-OS/pull/477",link:"Review build draft"},
 audit:{label:"Inspect Evidence",hint:"Local npm audit and safe remote-plan proposals.",source:"https://github.com/eggie-admin/LuHm-OS/pull/478",link:"Review audit draft"},
 settings:{label:"Settings",hint:"Session preferences only; no OS or browser registry edits.",source:"https://github.com/eggie-admin/LuHm-OS/pull/476",link:"Review web kiosk draft"}
};
let counts=initialCounts();const tasks=document.getElementById("tasks"),selection=document.getElementById("selection"),
status=document.getElementById("status");
function render(){
 tasks.replaceChildren();
 for(const id of sortActions(counts)){
  const item=details[id], card=document.createElement("article");card.className="task";card.setAttribute("role","listitem");
  const title=document.createElement("h3");title.textContent=item.label;
  const button=document.createElement("button");button.type="button";button.textContent=item.label;
  button.addEventListener("click",()=>{
   counts=selectAction(counts,id);
   selection.textContent=item.label+" selected "+counts[id]+" time(s) in this tab.";
   status.textContent="This is a local selection receipt. Use the source review link below for the actual candidate.";
   render();
  });
  const p=document.createElement("p");p.textContent=item.hint;
  const a=document.createElement("a");a.href=item.source;a.target="_blank";a.rel="noopener noreferrer";
  a.textContent=item.link;
  const badge=document.createElement("span");badge.className="count";badge.textContent="Session uses: "+counts[id];
  card.append(title,button,p,a,document.createElement("br"),badge);
  tasks.appendChild(card);
 }
}
document.getElementById("reset").addEventListener("click",()=>{
 counts=initialCounts();render();selection.textContent="Order reset to first-time studio defaults.";
 status.textContent="Only this page's counters were cleared.";
});
render();
