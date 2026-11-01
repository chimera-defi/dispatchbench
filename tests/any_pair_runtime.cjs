// R3: execute the restored historical widget using its real page JSON payload.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const payload=JSON.parse(fs.readFileSync(0,'utf8'));
class Element {
 constructor(){this.innerHTML='';this.clientWidth=760;this.options=[];this.firstChild={};}
 add(option){this.options.push(option)} appendChild(){} querySelectorAll(){return []}
}
const elements=new Map();const el=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id)};
const document={getElementById:id=>id==='data'?{textContent:JSON.stringify({any_pair:payload.data})}:el(id),
 createElement:tag=>tag==='canvas'?{getContext:()=>({measureText:text=>({width:text.length*7})})}:new Element()};
const context={document,window:{addEventListener(){}},localStorage:{getItem(){return null},setItem(){}},
 getComputedStyle:()=>({fontFamily:'Inter'}),Option:function(text,value){this.text=text;this.value=value},console};
vm.createContext(context);
let code=payload.html.split('<script>')[1].split('</script>')[0];
code=code.replace('draw()})();','globalThis.pairHarness={draw,st,M,D};draw()})();');
vm.runInContext(code,context);
const h=context.pairHarness;assert(h);assert.equal(el('pair-ex').options.length,5);
assert.equal(el('pair-ey').options.length,5);let scenarios=0;
for(const width of [390,1280])for(const x of Object.keys(h.M))for(const y of Object.keys(h.M))for(const log of [false,true]){
 el('xplot').clientWidth=width;Object.assign(h.st,{x,y,lx:log,ly:log});h.draw();scenarios++;
 const html=el('xplot').innerHTML;
 assert(html.includes('role="img"'));assert(!/NaN|undefined|Infinity/.test(html),`${width}/${x}/${y}/${log}`);
 assert(html.includes(h.M[x].l)&&html.includes(h.M[y].l));
 assert((html.match(/class="explorer-point"/g)||[]).length>0);
}
h.D.forEach(row=>h.st.off[row.c]=true);h.draw();assert(el('xplot').innerHTML.includes('No configs selected.'));
assert(!Object.keys(context).some(key=>['X','D','st','draw'].includes(key)),'legacy variables must remain local');
console.log(`${scenarios} any-pair axis/width/log scenarios; empty selection and namespace checks pass`);
