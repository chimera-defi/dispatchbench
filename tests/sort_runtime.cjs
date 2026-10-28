// Run the shipped script with a minimal DOM; native buttons supply Enter/Space
// activation in the browser, which reaches the same click handler exercised here.
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
class Element{
 constructor(tag,text=''){this.tagName=tag.toUpperCase();this.childNodes=[];this.parentNode=null;this.attrs={};this.text=text;this.classList={contains:c=>this.className===c}}
 get firstChild(){return this.childNodes[0]||null}
 get textContent(){return this.text+this.childNodes.map(n=>n.textContent).join('')}
 appendChild(node){
  if(node.parentNode){const siblings=node.parentNode.childNodes;siblings.splice(siblings.indexOf(node),1)}
  this.childNodes.push(node);node.parentNode=this;return node;
 }
 setAttribute(k,v){this.attrs[k]=String(v)}
 getAttribute(k){return this.attrs[k]??null}
 removeAttribute(k){delete this.attrs[k]}
 click(){if(this.onclick)this.onclick()}
}
function row(values,group=false){
 const r=new Element('tr');if(group)r.className='grp';
 r.cells=values.map(text=>r.appendChild(new Element(group?'th':'td',text)));return r;
}
function body(rows){const b=new Element('tbody');rows.forEach(r=>b.appendChild(r));Object.defineProperty(b,'rows',{get:()=>b.childNodes});return b}
function table(){
 const tb=new Element('table'),headers=['Name','Score','Cost'].map(text=>{
  const th=new Element('th');th.appendChild(new Element('span',text));return th;
 });
 tb.tHead={rows:[{cells:headers}]};
 tb.tBodies=[body([row(['Main'],true),row(['Charlie','95% (57/60)','$0.00112']),row(['Alpha','12','$12']),row(['Bravo','1,569','$0.10']),row(['Delta','–','–']),row(['Echo','−3','~$2'])]),
  body([row(['Hard'],true),row(['Zulu','2','$20']),row(['Xray','1','$10'])])];return tb;
}
const tables=[table(),table()],originalLabels=tables.map(t=>t.tHead.rows[0].cells.map(th=>th.firstChild));
const document={
 getElementById:id=>id==='data'?{textContent:'{"explorer":{"tie":{}}}'}:null,
 createElement:tag=>new Element(tag),
 querySelectorAll:selector=>selector==='table.sortable'?tables:[],
 addEventListener(){}
};
vm.runInNewContext(fs.readFileSync('docs/page/sort.js','utf8'),{document,window:{addEventListener(){}},console});
for(const [t,tb] of tables.entries()){
 for(const [i,th] of tb.tHead.rows[0].cells.entries()){
  assert.equal(th.childNodes.length,1,'each sortable header must contain exactly one button');
  const button=th.firstChild;
  assert.equal(button.tagName,'BUTTON','each sortable header must contain a native button');
  assert.equal(button.type,'button');assert.equal(button.className,'sort-btn');
  assert.equal(button.firstChild,originalLabels[t][i],'existing header markup must be preserved');
  assert.equal(th.getAttribute('aria-sort'),'none');assert.equal(th.onclick,undefined);
 }
}
const headers=tables[0].tHead.rows[0].cells,states=()=>headers.map(th=>th.getAttribute('aria-sort'));
const names=b=>b.rows.slice(1).map(r=>r.cells[0].textContent),groups=tables[0].tBodies.map(b=>b.rows[0]);
headers[1].firstChild.click();assert.deepEqual(states(),['none','ascending','none']);
assert.deepEqual(names(tables[0].tBodies[0]),['Echo','Alpha','Charlie','Bravo','Delta']);
assert.deepEqual(names(tables[0].tBodies[1]),['Xray','Zulu']);
headers[1].firstChild.click();assert.deepEqual(states(),['none','descending','none']);
assert.deepEqual(names(tables[0].tBodies[0]),['Bravo','Charlie','Alpha','Echo','Delta']);
assert.deepEqual(names(tables[0].tBodies[1]),['Zulu','Xray']);
headers[0].firstChild.click();assert.deepEqual(states(),['ascending','none','none']);
assert.deepEqual(names(tables[0].tBodies[0]),['Alpha','Bravo','Charlie','Delta','Echo']);
headers[0].firstChild.click();assert.deepEqual(names(tables[0].tBodies[0]),['Echo','Delta','Charlie','Bravo','Alpha']);
headers[2].firstChild.click();assert.deepEqual(states(),['none','none','ascending']);
assert.deepEqual(names(tables[0].tBodies[0]),['Charlie','Bravo','Echo','Alpha','Delta']);
headers[2].firstChild.click();assert.deepEqual(names(tables[0].tBodies[0]),['Alpha','Echo','Bravo','Charlie','Delta']);
for(const [i,b] of tables[0].tBodies.entries())assert.equal(b.rows[0],groups[i],'group headings must stay first');
assert(tables[1].tHead.rows[0].cells.every(th=>th.getAttribute('aria-sort')==='none'),'other tables must stay unsorted');
assert.deepEqual(names(tables[1].tBodies[0]),['Charlie','Alpha','Bravo','Delta','Echo']);
console.log('sortable headers: native buttons, initial/reset ARIA states, numeric/text/currency ordering, missing values and separate groups/tables pass');
