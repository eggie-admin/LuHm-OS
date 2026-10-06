"use strict";
(function(){
  const MAX_LINES=120;
  const state={history:[],historyIndex:0,commands:[],root:null,thread:null,input:null,marker:null};

  function byRole(root,role){return root.querySelector('[data-role="'+role+'"]')}

  function clampLines(){
    if(!state.thread)return;
    while(state.thread.children.length>MAX_LINES)state.thread.removeChild(state.thread.firstElementChild);
  }

  function appendLine(kind,text,meta){
    if(!state.thread)return;
    const line=document.createElement("article");
    line.className="staticChatLine "+kind;
    line.dataset.kind=kind;
    const head=document.createElement("div");
    head.className="staticChatMeta";
    const stamp=document.createElement("span");
    stamp.textContent=new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"});
    const tag=document.createElement("span");
    tag.textContent=String(kind||"chat").toUpperCase();
    head.append(tag,stamp);
    if(meta){
      const extra=document.createElement("span");
      extra.textContent=String(meta).slice(0,80);
      head.append(extra);
    }
    const body=document.createElement("div");
    body.className="staticChatBody";
    body.textContent=String(text||"");
    const actions=document.createElement("div");
    actions.className="staticChatActions";
    for(const action of ["copy","explain"]){
      const button=document.createElement("button");
      button.type="button";
      button.dataset.action=action;
      button.textContent=action.toUpperCase();
      actions.appendChild(button);
    }
    line.append(head,body,actions);
    state.thread.appendChild(line);
    clampLines();
    line.scrollIntoView({block:"nearest"});
    return line;
  }

  function markProved(text){
    if(!state.marker)return;
    state.marker.textContent="LAST PROVED STATE · "+String(text||"checkpoint").slice(0,96);
    state.marker.dataset.state="proved";
  }

  function commandRows(config){
    const rows=config?.precisionCommands?.examples;
    return Array.isArray(rows)?rows.filter(row=>row&&row.debugVerb&&row.kebab&&row.camelHump):[];
  }

  function commandNames(config){
    const names=[];
    for(const row of commandRows(config)){
      names.push("/"+String(row.debugVerb).toLowerCase());
      names.push("/"+String(row.kebab).toLowerCase());
    }
    return [...new Set(names)].sort();
  }

  function completeInput(){
    if(!state.input)return;
    const raw=state.input.value;
    const token=raw.trim().split(/\s+/).pop()||"";
    if(!token.startsWith("/"))return;
    const matches=state.commands.filter(x=>x.startsWith(token.toLowerCase()));
    if(matches.length===1){
      const prefix=raw.slice(0,raw.length-token.length);
      state.input.value=prefix+matches[0]+" ";
    }
  }

  function historyStep(direction){
    if(!state.input||!state.history.length)return;
    state.historyIndex=Math.max(0,Math.min(state.history.length,state.historyIndex+direction));
    state.input.value=state.historyIndex===state.history.length?"":state.history[state.historyIndex];
    queueMicrotask(()=>state.input.setSelectionRange(state.input.value.length,state.input.value.length));
  }

  async function sendFollowUp(text){
    if(window.openai?.sendFollowUpMessage){
      return window.openai.sendFollowUpMessage({prompt:text});
    }
    window.dispatchEvent(new CustomEvent("luhm:static-chat:command",{detail:{text}}));
    return null;
  }

  async function submit(){
    if(!state.input)return;
    const text=state.input.value.trim();
    if(!text)return;
    state.history.push(text);
    if(state.history.length>32)state.history.shift();
    state.historyIndex=state.history.length;
    state.input.value="";
    appendLine("chat",text,"Professor");
    const normalized=text.toLowerCase();
    const known=!normalized.startsWith("/")||state.commands.some(cmd=>normalized===cmd||normalized.startsWith(cmd+" "));
    if(!known){
      appendLine("control","VERIFY · unknown command. No action executed.","resolver");
      return;
    }
    appendLine("control","Forwarding through the bounded follow-up bridge.","router");
    try{
      await sendFollowUp(text);
    }catch(error){
      appendLine("proof","VERIFY · follow-up bridge unavailable: "+String(error?.message||error),"host");
    }
  }

  function wireContextActions(){
    state.thread?.addEventListener("click",async event=>{
      const button=event.target.closest("[data-action]");
      const line=event.target.closest(".staticChatLine");
      if(!button||!line)return;
      const text=line.querySelector(".staticChatBody")?.textContent||"";
      if(button.dataset.action==="copy"){
        try{
          await navigator.clipboard?.writeText(text);
          button.textContent="COPIED";
        }catch(_){
          button.textContent="SELECT";
        }
      }else if(button.dataset.action==="explain"){
        await sendFollowUp("Explain this LuHm chat line using current doctrine and preserve authority boundaries: "+text);
      }
    });
  }

  function renderBootstrap(config){
    const source=config?.runtimeReceipt?.sourceRef||config?.crownFlow?.sourceRef||"VERIFY";
    const opening=config?.openingDay?.status||"VERIFY";
    appendLine("control","STATIC CHAT FOCUS LAB · source "+source,"bootstrap");
    appendLine("chat","Chat lines stay conversational. Tool, proof, and control lines stay visibly distinct.","class map");
    appendLine("proof","Opening Day contract: "+opening+". Visual state does not establish GREEN.","evidence");
    appendLine("control","HEAR → RESOLVE → ACT → VERIFY","4:4 meter");
    markProved(source);
  }

  function mount(root,config){
    if(!root||root.dataset.mounted==="true")return;
    root.dataset.mounted="true";
    state.root=root;
    state.thread=byRole(root,"thread");
    state.input=byRole(root,"input");
    state.marker=byRole(root,"marker");
    state.commands=commandNames(config);
    state.historyIndex=0;
    renderBootstrap(config);
    wireContextActions();
    const send=byRole(root,"send");
    send?.addEventListener("click",submit);
    state.input?.addEventListener("keydown",event=>{
      if(event.key==="Enter"&&!event.shiftKey){event.preventDefault();submit();}
      else if(event.key==="ArrowUp"){event.preventDefault();historyStep(-1);}
      else if(event.key==="ArrowDown"){event.preventDefault();historyStep(1);}
      else if(event.key==="Tab"){event.preventDefault();completeInput();}
    });
  }

  async function autoMount(){
    const root=document.querySelector("[data-luhm-static-chat]");
    if(!root)return;
    try{
      const response=await fetch("/harness/config.json",{cache:"no-store"});
      if(!response.ok)throw new Error("config "+response.status);
      const config=await response.json();
      if(config?.staticChat?.schema!=="luhmOs.staticChatTransmogrifier.v1")throw new Error("static chat schema");
      mount(root,config);
    }catch(error){
      state.root=root;
      state.thread=byRole(root,"thread");
      state.input=byRole(root,"input");
      state.marker=byRole(root,"marker");
      appendLine("proof","VERIFY · static chat config unavailable: "+String(error?.message||error),"bootstrap");
    }
  }

  window.LuhmStaticChat=Object.freeze({mount,appendLine,markProved});
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",autoMount,{once:true});
  else autoMount();
})();
