// Execute the shipped interaction code against a minimal local DOM. Geometry and
// data behaviour are tested here; real browser layout remains a separate check.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
// R6: direct invocation uses the shipped page and independent canonical data;
// pytest can still supply mutated fixtures through stdin.
const input=fs.readFileSync(0,'utf8');
const payload=input.trim()?JSON.parse(input):{
 explorer:JSON.parse(fs.readFileSync('results/report/page.html','utf8').match(/<script type="application\/json" id="data">([\s\S]*?)<\/script>/)[1]).explorer,
 expected:JSON.parse(fs.readFileSync('results/dataset.json','utf8')).explorer
};
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
    assert(!html.includes('ex-leader')&&!html.includes('ex-label-clip'),'no name column or leaders');
    const frontier=projected.filter(r=>m.get(r.key).on_frontier).sort((a,b)=>{
     const k=exp.views[view].objectives[0][0],v=r=>k==='cost'?(quota?r.quota_usd_per_pass:r.usd_per_pass):r[k];
     return v(a)-v(b)||a.key.localeCompare(b.key);
    });
    const keys=source=>Array.from(source.matchAll(/class="ex-number" data-key="([^"]+)"/g),m=>m[1].replaceAll('&amp;','&'));
    assert.deepEqual(keys(html),frontier.map(r=>r.key));
    const chipKeys=source=>Array.from(source.matchAll(/data-key="([^"]+)"/g),m=>m[1].replaceAll('&amp;','&'));
    assert.deepEqual(chipKeys(element('ex-chips').innerHTML),frontier.map(r=>r.key));
    assert.deepEqual(chipKeys(element('ex-best').innerHTML),frontier.map(r=>r.key));
    const points=Array.from(html.matchAll(/data-x="([^"]+)" data-y="([^"]+)"/g),m=>[+m[1],+m[2]]);
    // R8: existence in the SVG is insufficient when the annotation clip hides a badge.
    const clip=html.match(/<clipPath id="ex-clip"><rect x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)"/).slice(1).map(Number);
    const within=([l,t,r,b])=>l>=clip[0]-1e-8&&t>=clip[1]-1e-8&&r<=clip[0]+clip[2]+1e-8&&b<=clip[1]+clip[3]+1e-8;
    const rings=Array.from(html.matchAll(/<circle class="ex-number-ring" cx="([^"]+)" cy="([^"]+)" r="([^"]+)"/g),m=>m.slice(1).map(Number));
    assert.equal(rings.length,frontier.length);
    const badgeBoxes=[];
    rings.forEach(([x,y,r],i)=>{
     const box=[x-r-1,y-r-1,x+r+1,y+r+1];
     assert(within(box),`${width}/${set.id}/${quota}/${view}/${frontier[i].key} clipped badge: ${box}`);
     for(const [l,t,rr,b] of badgeBoxes)assert(!(box[0]<rr&&l<box[2]&&box[1]<b&&t<box[3]),'badges overlap, including coincident frontier points');
     badgeBoxes.push(box);
    });
    const labels=Array.from(html.matchAll(/<text ([^>]*class="ex-label"[^>]*)>/g));
    assert(labels.length<=3);if(width<=480)assert.equal(labels.length,0);
    for(const match of html.matchAll(/<text ([^>]*class="ex-(?:label|number)"[^>]*)>/g)){
     const a=Object.fromEntries(Array.from(match[1].matchAll(/([\w-]+)="([^"]*)"/g),m=>[m[1],m[2]]));
     const w=+a['data-width'],x=+a.x,y=+a.y,left=x-(a['text-anchor']==='end'?w:a['text-anchor']==='middle'?w/2:0);
     if(a.class==='ex-number')assert(within([left,y-12,left+w,y+3]),`${width}/${set.id}/${quota}/${view} clipped number text`);
     for(const [px,py] of points)assert(!(left<px+12&&px-12<left+w&&y-12<py+12&&py-12<y+3),`${set.id}/${view} label overlaps mark`);
    }

   }
  }
 }
}
h.st.set=exp.default_set;h.st.view='front';h.st.quota=true;h.st.minPass=1;h.render();
const rr=exp.sets.find(s=>s.id===h.st.set).rows.map(k=>rm.get(k));
const exact=rr.filter(r=>r.pass_rate===1&&r.quota_usd_per_pass===0&&r.cost_kind!=='unmetered');
assert(exact.length>1);const chips=element('ex-best').innerHTML;assert.equal((chips.match(/<li>/g)||[]).length,h.members(rr).size ? rr.filter(r=>h.members(rr).get(r.key).on_frontier).length : 0);for(const r of exact)assert(chips.includes(r.display.replaceAll('&','&amp;')));
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
 return {html,plot:rect('ex-clip'),points:new Map(Array.from(html.matchAll(/data-key="([^"]+)" data-x="([^"]+)" data-y="([^"]+)"/g),m=>[m[1],[+m[2],+m[3]]]))};
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
   assert(!after.html.includes('ex-label-clip'));
   assert(!after.html.includes('ex-leader'));
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
