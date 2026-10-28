// Execute the shipped interaction code against a minimal local DOM. Geometry and
// data behaviour are tested here; real browser layout remains a separate check.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const payload=JSON.parse(fs.readFileSync(0,'utf8'));
class Element{
 constructor(){this.innerHTML='';this.dataset={};this.clientWidth=760;this.attrs={};this.childElementCount=0;this.classList={toggle(){}};this.viewBox={baseVal:{width:760,height:480}}}
 querySelector(){return null}querySelectorAll(){return []}setAttribute(k,v){this.attrs[k]=v}insertAdjacentHTML(){}getBoundingClientRect(){return {width:this.clientWidth,height:480,left:0,top:0}}}
const elements=new Map();function element(id){if(!elements.has(id))elements.set(id,new Element());return elements.get(id)}
const root=element('pareto-explorer');root.querySelector=s=>s.includes(' svg')?null:element(s.slice(1));
const doc={addEventListener:(e,f)=>f(),getElementById:id=>id==='data'?{textContent:JSON.stringify({explorer:payload.explorer})}:root};
let code=fs.readFileSync('docs/page/explorer.html','utf8').split('<script>')[1].split('</script>')[0];
code=code.replace("render();root.dataset.ready='true';","render();root.dataset.ready='true';globalThis.harness={st,render,members,eligible,dominates,geometry};");
const context={document:doc,window:{addEventListener(){}},console};vm.createContext(context);vm.runInContext(code,context);
const h=context.harness,exp=payload.explorer,canonical=payload.expected||exp,rm=new Map(exp.rows.map(r=>[r.key,r]));let scenarios=0;
for(const width of [760,350]){element('ex-chart').clientWidth=width;
 for(const set of exp.sets){h.st.set=set.id;h.st.off.clear();
  for(const quota of [false,true]){h.st.quota=quota;
   for(const view of Object.keys(exp.views)){h.st.view=view;h.render();scenarios++;
    const rr=set.rows.map(k=>rm.get(k)),m=h.members(rr),expected=canonical.sets.find(s=>s.id===set.id).views[quota?'quota':'list'][view].membership;
    for(const r of rr){assert.equal(m.get(r.key).on_frontier,expected[r.key].on_frontier,`${set.id}/${quota}/${view}/${r.key}`);assert.equal(m.get(r.key).eligible,expected[r.key].eligible);assert.deepEqual(Array.from(m.get(r.key).beaten_by,r=>r.key).sort(),expected[r.key].beaten_by.slice().sort())}
    const html=element('ex-chart').innerHTML;
    assert(html.includes(`viewBox="0 0 ${width} 480"`));
    assert(!/NaN|Infinity|undefined/.test(html),`${set.id}/${quota}/${view} invalid geometry`);
    const projected=rr.filter(r=>!exp.views[view].objectives.some(([k])=>k==='cost')||r.cost_kind!=='unmetered'&&(quota?r.quota_usd_per_pass:r.usd_per_pass)!=null);
    assert.equal((html.match(/class="(?:ex-par )?ex-point/g)||[]).length,projected.length,`${set.id}/${view} missing points`);
    assert.equal((element('ex-radar-grid').innerHTML.match(/class="card ex-radar"/g)||[]).length,rr.length);
   }
  }
 }
}
h.st.set=exp.default_set;h.st.view='front';h.st.quota=true;h.st.minPass=1;h.render();
const rr=exp.sets.find(s=>s.id===h.st.set).rows.map(k=>rm.get(k));
const exact=rr.filter(r=>r.pass_rate===1&&r.quota_usd_per_pass===0&&r.cost_kind!=='unmetered');
assert(exact.length>1);const chips=element('ex-best').innerHTML;assert(chips.includes(' = '));for(const r of exact)assert(chips.includes(r.display.replaceAll('&','&amp;')));
h.st.off=new Set(rr.map(r=>r.key));h.render();assert(element('ex-chart').innerHTML.includes('No configs match'));
h.st.off.clear();h.st.quota=false;h.st.minPass=0;h.st.view='side';h.render();assert(element('ex-chart').innerHTML.includes('devin16slow-default'));
assert(element('ex-model-grid').innerHTML.includes('<h4>devin</h4>'));
h.st.prereg=true;h.render();assert(!element('ex-chart').innerHTML.includes('devin16slow-default'));
h.st.prereg=false;h.st.facets.add('family:Codex');h.render();assert(!element('ex-chart').innerHTML.includes('main/terra61-low@'));
// Drive the shipped wheel handler around haiku-high across the label threshold.
// Predict the visible domain from pre-zoom coordinates, independently of geometry().
h.st.facets.clear();h.st.sel=h.st.hover=null;
const originalQuery=root.querySelector,svg=new Element();
root.querySelector=s=>s==='#ex-chart svg'?svg:element(s.slice(1));
const snapshot=()=>{
 const html=element('ex-chart').innerHTML;
 const rect=id=>html.match(new RegExp(`<clipPath id="${id}"><rect x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)"`)).slice(1).map(Number);
 return {html,plot:rect('ex-clip'),gutter:rect('ex-label-clip'),points:new Map(Array.from(html.matchAll(/data-key="([^"]+)" data-x="([^"]+)" data-y="([^"]+)"/g),m=>[m[1],[+m[2],+m[3]]]))};
};
const inside=([x,y],[l,t,w,h])=>x>=l-1e-8&&x<=l+w+1e-8&&y>=t-1e-8&&y<=t+h+1e-8;
let zoomScenarios=0;
for(const width of [760,390]){
 element('ex-chart').clientWidth=svg.clientWidth=svg.viewBox.baseVal.width=width;
 for(const view of ['front','top','side']){
  h.st.view=view;h.st.zk=1;h.st.zx=h.st.zy=0;h.render();
  const base=snapshot(),[anchorKey,anchor]=Array.from(base.points).find(([k])=>rm.get(k).config==='haiku-high');
  h.render();assert.equal(snapshot().html,base.html,'render must be deterministic');
  assert(inside(anchor,base.plot));
  for(const zoom of [2.1,2.2,3,2.1,1]){
   svg.onwheel({clientX:anchor[0],clientY:anchor[1],deltaY:-Math.log(zoom/h.st.zk)/.0015,preventDefault(){}});
   const after=snapshot();assert.deepEqual(after.plot,base.plot,`${width}/${view}/${zoom} plot moved`);
   assert(after.gutter[1]+after.gutter[3]<after.plot[1],'labels must be clipped above the plot');
   assert(after.html.includes('<g clip-path="url(#ex-label-clip)">'));
   let visible=0;
   for(const [key,[x,y]] of base.points){
    const expected=[x*h.st.zk+h.st.zx,y*h.st.zk+h.st.zy],actual=after.points.get(key);
    assert(actual,`${key} lost on zoom`);
    assert(Math.hypot(actual[0]-expected[0],actual[1]-expected[1])<1e-7,`${width}/${view}/${zoom}/${key} domain changed`);
    if(inside(expected,base.plot)){visible++;assert(inside(actual,after.plot),`${key} escaped plot`)}
   }
   assert(visible>0);
   const [ax,ay]=after.points.get(anchorKey);assert(Math.hypot(ax-anchor[0],ay-anchor[1])<1e-7,'zoom anchor moved');
   zoomScenarios++;
  }
 }
}
root.querySelector=originalQuery;
console.log(`${scenarios} set/view/pricing/width scenarios; ${zoomScenarios} wheel zoom scenarios; frontier parity, ties, points, radars and filters pass`);
