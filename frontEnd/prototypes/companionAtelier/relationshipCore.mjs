const FIELDS = ["trust", "affection", "jealousy"];
const ALLOWED = /^[a-z][A-Za-z0-9]{1,39}$/;
const copy = (item) => JSON.parse(JSON.stringify(item));

export function createRelationshipStore(rules, profiles) {
  if (rules?.schema !== "luhmOs.relationshipRules.v2" || profiles?.schema !== "luhmOs.originalCompanionProfiles.v1") throw Error("Unsupported relationship canon");
  if (!Array.isArray(profiles.companions) || profiles.companions.length !== 3) throw Error("Roster mismatch");
  const events = rules.events;
  if (!events || Object.keys(events).length !== 7) throw Error("Event contract mismatch");
  for (const delta of Object.values(events)) {
    if (!delta || FIELDS.some((field) => !Number.isInteger(delta[field]) || Math.abs(delta[field]) > 10)) throw Error("Invalid bounded event");
  }
  const byId = new Map();
  const state = new Map();
  const initial = rules.initial;
  if (FIELDS.some((field) => !Number.isInteger(initial?.[field]) || initial[field] < 0 || initial[field] > 100)) throw Error("Invalid initial state");
  for (const profile of profiles.companions) {
    if (profile.adult !== true || !ALLOWED.test(profile.id) || byId.has(profile.id)) throw Error("Invalid original companion");
    if (Object.keys(events).some((id) => typeof profile.dialogue?.[id] !== "string" || profile.dialogue[id].length > 220)) throw Error("Dialogue mismatch");
    byId.set(profile.id, copy(profile));
    state.set(profile.id, { stats:copy(initial),journal:[] });
  }
  const score = (s) => Math.min(100,Math.max(0,Math.trunc((s.trust + s.affection - s.jealousy) / 2)));
  function evaluate(id) {
    if (!byId.has(id)) return null;
    const current = state.get(id);
    const bondScore = score(current.stats);
    const bondTier = rules.tiers.reduce((name,t) => bondScore >= t.minScore ? t.id : name, "newcomer");
    return {
      schema:"luhmOs.relationshipSnapshot.v2",
      id,stats:copy(current.stats),journal:[...current.journal],
      bondScore,bondTier,rewards:rules.rewards.filter((r)=>bondScore>=r.minScore).map((r)=>r.id)
    };
  }
  function apply(id,eventId) {
    if (!byId.has(id) || !Object.hasOwn(events,eventId)) return {accepted:false,reason:"eventNotAllowed"};
    const current = state.get(id);
    const change = events[eventId];
    for (const field of FIELDS) current.stats[field] = Math.max(0,Math.min(100,current.stats[field]+change[field]));
    current.journal.push(eventId);
    if (current.journal.length>32) current.journal.shift();
    return {accepted:true,reaction:byId.get(id).dialogue[eventId],...evaluate(id)};
  }
  function restore(saved) {
    if (saved?.schema!=="luhmOs.relationshipSave.v2" || !Array.isArray(saved.items) || saved.items.length!==byId.size) return false;
    const incoming = new Map();
    for (const item of saved.items) {
      if (!item || !byId.has(item.id) || incoming.has(item.id) || !item.stats || !Array.isArray(item.journal) || item.journal.length>32) return false;
      if (FIELDS.some((f)=>!Number.isInteger(item.stats[f]) || item.stats[f]<0 || item.stats[f]>100)) return false;
      if (item.journal.some((id)=>!Object.hasOwn(events,id))) return false;
      incoming.set(item.id,{stats:copy(item.stats),journal:[...item.journal]});
    }
    for (const [id,s] of incoming) state.set(id,s);
    return true;
  }
  return Object.freeze({
    roster:()=>[...byId.values()].map(copy),
    evaluate,apply,
    save:()=>({schema:"luhmOs.relationshipSave.v2",items:[...byId.keys()].map((id)=>({id,...copy(state.get(id))}))}),
    restore,
    reset:()=>{for(const id of byId.keys())state.set(id,{stats:copy(initial),journal:[]});}
  });
}
