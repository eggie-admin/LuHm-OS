/* Pure, source-bound Aramoor graph. Browser art and Godot share the same JSON; no agent or network side effects. */
export function inspectAramoorWorld(world) {
  const zones=world?.zones, links=world?.links;
  if(world?.schema!=="luhmOs.aramoorArchipelago.v1" || !Array.isArray(zones) || !Array.isArray(links)) {
    throw new Error("INVALID_WORLD_SCHEMA");
  }
  if(zones.length!==9 || links.length!==12) throw new Error("INVALID_WORLD_BUDGET");
  if(world?.artPolicy?.publicAllowed!==false || world?.source?.adventureLicense!=="CC BY-SA 4.0" ||
     world?.source?.modulePdfInspected!==false || world?.gates?.crown!=="STOP") throw new Error("RIGHTS_OR_CROWN_HOLD");
  const byId=new Map();
  for(const zone of zones) {
    if(!zone || typeof zone.id!=="string" || !/^[a-zA-Z][a-zA-Z0-9]+$/.test(zone.id) || byId.has(zone.id)) {
      throw new Error("BAD_OR_DUPLICATE_ZONE");
    }
    if(!Array.isArray(zone.grid) || zone.grid.length!==2 ||
       !zone.grid.every(n=>Number.isInteger(n)&&n>=0&&n<=2) ||
       typeof zone.beat!=="string" || !zone.beat || !/^#[0-9a-fA-F]{6}$/.test(zone.accent)) {
      throw new Error("INVALID_ZONE_METADATA");
    }
    byId.set(zone.id,zone);
  }
  const neighbors=new Map([...byId.keys()].map(id=>[id,new Set()]));
  const signatures=new Set();
  for(const edge of links) {
    if(!Array.isArray(edge) || edge.length!==2 || !byId.has(edge[0]) || !byId.has(edge[1]) || edge[0]===edge[1]) throw new Error("BROKEN_WORLD_EDGE");
    const signature=[...edge].sort().join("::");
    if(signatures.has(signature)) throw new Error("DUPLICATE_WORLD_EDGE");
    signatures.add(signature);
    neighbors.get(edge[0]).add(edge[1]); neighbors.get(edge[1]).add(edge[0]);
  }
  const seen=new Set(),queue=[zones[0].id];
  while(queue.length) {
    const node=queue.shift();
    if(seen.has(node)) continue;
    seen.add(node);
    queue.push(...neighbors.get(node));
  }
  if(seen.size!==zones.length) throw new Error("DISCONNECTED_ARCHIPELAGO");
  return Object.freeze({zones:zones.length,bridges:links.length,tides:world.worlds?.length??0,byId,neighbors});
}

export function travelBetween(world,fromId,toId) {
  const graph=inspectAramoorWorld(world);
  if(!graph.byId.has(fromId) || !graph.byId.has(toId)) return Object.freeze({ok:false,reason:"UNKNOWN_REGION",zoneId:fromId});
  if(fromId===toId) return Object.freeze({ok:true,reason:"ALREADY_HERE",zoneId:fromId});
  if(!graph.neighbors.get(fromId).has(toId)) return Object.freeze({ok:false,reason:"BRIDGE_NOT_CONNECTED",zoneId:fromId});
  return Object.freeze({ok:true,reason:"CROSSING_COMPLETE",zoneId:toId});
}

export function reachableRegions(world,zoneId) {
  const graph=inspectAramoorWorld(world);
  if(!graph.byId.has(zoneId)) return [];
  return [...graph.neighbors.get(zoneId)];
}
