import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";
const root=resolve(dirname(fileURLToPath(import.meta.url)),"../../..");
function inspect(pkg,lock){
 const errors=[];
 const add=x=>errors.push(x);
 if(pkg.private!==true)add("PUBLIC");
 if(lock.lockfileVersion!==3)add("LOCK_FORMAT");
 if(pkg.name!==lock.name||pkg.version!==lock.version)add("ROOT_DRIFT");
 if(lock.packages?.[""]?.name!==pkg.name||lock.packages?.[""]?.version!==pkg.version)add("LOCK_ROOT");
 for(const k of ["preinstall","install","postinstall","prepare","prepack","postpack","prepublish","prepublishOnly"])
   if(Object.hasOwn(pkg.scripts??{},k))add("LIFECYCLE");
 const deps={...(pkg.dependencies??{}),...(pkg.devDependencies??{})};
 for(const [name,version] of Object.entries(deps)){
   if(!/^\d+\.\d+\.\d+(?:-[\w.-]+)?$/.test(version))add("UNPINNED");
   const kind=Object.hasOwn(pkg.devDependencies??{},name)?"devDependencies":"dependencies";
   if(lock.packages?.[""]?.[kind]?.[name]!==version)add("DECLARATION_DRIFT");
   const item=lock.packages?.[`node_modules/${name}`];
   if(!item||item.version!==version){add("VERSION_DRIFT");continue;}
   if(!/^https:\/\/registry\.npmjs\.org\//.test(item.resolved??""))add("SOURCE_DRIFT");
   if(!/^sha512-[A-Za-z0-9+/]+={0,2}$/.test(item.integrity??""))add("INTEGRITY");
   if(typeof item.license!=="string"||!item.license.trim())add("LICENSE_METADATA");
 }
 for(const key of Object.keys(lock.packages??{}))
   if(key&&(!key.startsWith("node_modules/")||!Object.hasOwn(deps,key.slice(13))))add("UNREVIEWED_EXTRA");
 return errors;
}
const p={name:"x",version:"1.0.0",private:true,dependencies:{jquery:"3.7.1"}};
const l={name:"x",version:"1.0.0",lockfileVersion:3,packages:{
 "":{name:"x",version:"1.0.0",dependencies:{jquery:"3.7.1"}},
 "node_modules/jquery":{version:"3.7.1",resolved:"https://registry.npmjs.org/jquery/-/jquery-3.7.1.tgz",integrity:"sha512-AAAA",license:"MIT"}}};
const copy=x=>structuredClone(x);
test("valid locked package metadata",()=>assert.deepEqual(inspect(p,l),[]));
test("reject range version",()=>{const x=copy(p);x.dependencies.jquery="^3.7.1";assert.ok(inspect(x,l).includes("UNPINNED"));});
test("reject version drift",()=>{const x=copy(l);x.packages["node_modules/jquery"].version="3.7.0";assert.ok(inspect(p,x).includes("VERSION_DRIFT"));});
test("reject missing integrity",()=>{const x=copy(l);delete x.packages["node_modules/jquery"].integrity;assert.ok(inspect(p,x).includes("INTEGRITY"));});
test("reject remote source",()=>{const x=copy(l);x.packages["node_modules/jquery"].resolved="https://evil.invalid/a";assert.ok(inspect(p,x).includes("SOURCE_DRIFT"));});
test("reject lifecycle scripts",()=>{const x=copy(p);x.scripts={postinstall:"node x.js"};assert.ok(inspect(x,l).includes("LIFECYCLE"));});
test("reject unknown lockfile packages",()=>{const x=copy(l);x.packages["node_modules/extra"]={};assert.ok(inspect(p,x).includes("UNREVIEWED_EXTRA"));});
test("reject absent license",()=>{const x=copy(l);delete x.packages["node_modules/jquery"].license;assert.ok(inspect(p,x).includes("LICENSE_METADATA"));});
test("actual repository metadata is bounded",()=>{
 for(const name of ["frontEnd","packages/unified-ops"]){
  const pkg=JSON.parse(readFileSync(resolve(root,name,"package.json"),"utf8"));
  const lock=JSON.parse(readFileSync(resolve(root,name,"package-lock.json"),"utf8"));
  assert.deepEqual(inspect(pkg,lock),[],name);
  assert.equal(pkg.private,true);
  if(name==="frontEnd"){
   assert.deepEqual(pkg.dependencies,{jquery:"3.7.1"});
   assert.equal(lock.packages["node_modules/jquery"].license,"MIT");
  }else{assert.deepEqual(pkg.dependencies,{});assert.deepEqual(pkg.devDependencies,{});}
 }
});
