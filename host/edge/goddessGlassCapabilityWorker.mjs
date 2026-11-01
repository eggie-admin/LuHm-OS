/** Optional Cloudflare-compatible same-origin capability endpoint. Not deployed. */
const descriptor=Object.freeze({
  schema:"luhmOs.goddessGlassCapabilities.v1",
  source:"OPTIONAL_EDGE_SOURCE_ONLY",
  runtime:"NOT_ATTESTED",
  sqlAccess:"BACKEND_ONLY",
  cloudflareActive:false,
  writeAuthority:false,
  capabilities:[
    {id:"glassViewer",status:"localReady"},
    {id:"assetCatalog",status:"notConnected"},
    {id:"renderStatus",status:"notConnected"},
    {id:"studioReceipts",status:"notConnected"}
  ]
});
const body=JSON.stringify(descriptor);
export default {
  async fetch(request) {
    const url=new URL(request.url);
    if(url.pathname!=="/api/glass/capabilities")
      return new Response("Not Found",{status:404,headers:{"cache-control":"no-store"}});
    if(request.method!=="GET")
      return new Response("Method Not Allowed",{status:405,headers:{"allow":"GET","cache-control":"no-store"}});
    return new Response(body,{status:200,headers:{
      "content-type":"application/json; charset=utf-8",
      "cache-control":"no-store, private",
      "x-content-type-options":"nosniff"
    }});
  }
};