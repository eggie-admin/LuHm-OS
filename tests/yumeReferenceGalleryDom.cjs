// Requires jsdom in the test environment. No external assets are fetched.
const {JSDOM}=require('jsdom');
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../frontEnd/yumeReferenceGallery.html'),'utf8');
function create(stored='[]') {
  return new JSDOM(html,{url:'https://gallery.test/',runScripts:'dangerously',beforeParse(w){
    w.localStorage.setItem('luhm.yumeReferenceShortlist.v1',stored);
  }});
}
const dom=create(), w=dom.window, d=w.document;
const visible=()=>[...d.querySelectorAll('.card')].filter(c=>!c.hidden);
const input=(id,value)=>{d.getElementById(id).value=value;d.getElementById(id).dispatchEvent(new w.Event('input'));};
const click=id=>d.getElementById(id).click();
assert.equal(visible().length,29);
input('game','Fallout 4');assert.equal(visible().length,13);
input('kind','Engineering tool');assert.equal(visible().length,6);
click('reset');input('query','hair');assert(visible().length>0);assert(visible().every(c=>c.dataset.search.includes('hair')));
input('query','nothingcanmatchthis');assert.equal(visible().length,0);assert.equal(d.getElementById('empty').hidden,false);
click('reset');d.querySelector('.save').click();click('shortlist');assert.equal(visible().length,1);
const stored=w.localStorage.getItem('luhm.yumeReferenceShortlist.v1');assert.equal(JSON.parse(stored).length,1);
const reload=create(stored);assert.match(reload.window.document.getElementById('count').textContent,/1 shortlisted/);reload.window.close();
let blob,download;
w.URL.createObjectURL=b=>{blob=b;return 'blob:gallery-test'};w.URL.revokeObjectURL=()=>{};
w.HTMLAnchorElement.prototype.click=function(){download=this.download};
click('export');assert.equal(download,'yumeReferenceShortlist.json');assert.equal(blob.type,'application/json');
const reader=new w.FileReader();reader.onload=()=>{
 const data=JSON.parse(reader.result);assert.equal(data.cards.length,1);assert.equal(data.assetApproval,false);
 const corrupt=create('{}');assert.equal(corrupt.window.document.querySelectorAll('.card').length,29);assert.equal(corrupt.window.document.getElementById('notice').hidden,false);corrupt.window.close();
 dom.window.close();console.log('PASS: filters, empty state, shortlist persistence/export, corrupt storage recovery (DOM only; no layout claim)');
};reader.readAsText(blob);
