// Click a column header to sort its table; click again to reverse. Numbers sort as numbers ("95% (57/60)" sorts by 95,
// "$0.00112" by 0.00112, "1,569" by 1569); a column whose cells are not numbers sorts as text; "–" goes last either way.
// Each tbody sorts on its own, under its "grp" heading row, so the all-problems and hard-set groups never mix.
(function(){
// A cell is numeric only when it starts with a number (after ≥, ~, $ or a sign), so "sol61-medium" sorts as text.
function key(td){var t=td.textContent.replace(/,/g,"").replace(/−/g,"-").trim();var m=t.match(/^[≥≤~]?\$?([+-]?\d+(\.\d+)?)/);return m?parseFloat(m[1]):null}
document.querySelectorAll("table.sortable").forEach(function(tb){
 var ths=tb.tHead.rows[0].cells;
 Array.prototype.forEach.call(ths,function(th,i){th.title="Sort by this column";th.onclick=function(){
  var desc=th.getAttribute("aria-sort")==="ascending";Array.prototype.forEach.call(ths,function(h){h.removeAttribute("aria-sort")});
  th.setAttribute("aria-sort",desc?"descending":"ascending");
  Array.prototype.forEach.call(tb.tBodies,function(body){
  var rows=Array.prototype.filter.call(body.rows,function(r){return !r.classList.contains("grp")});
  rows.sort(function(a,b){var x=key(a.cells[i]),y=key(b.cells[i]);
   var ta=a.cells[i].textContent.trim(),tb2=b.cells[i].textContent.trim();
   if(ta==="–"||tb2==="–")return ta===tb2?0:ta==="–"?1:-1;
   if(x===null||y===null){var s=ta.localeCompare(tb2);return desc?-s:s}
   return desc?y-x:x-y});
  rows.forEach(function(r){body.appendChild(r)})})}})})})();
// Chart hover: a point and its key row share data-c. Hover or focus either one to highlight both and dim the rest; data-tip
// shows in .ctip. Tap works the same on touch; Escape or a tap outside clears it.
(function(){
document.querySelectorAll(".cwrap").forEach(function(w){
 var tip=w.querySelector(".ctip"),SEL=".pt,.ckey li,.picks li",all=function(){return w.querySelectorAll(SEL)};
 function clear(){w.classList.remove("hov");all().forEach(function(e){e.classList.remove("hi","dim")});tip.hidden=true}
 function updateCategories(set){
  w.querySelectorAll('.category-filter input').forEach(function(input){
   var empty=!w.querySelector('.s-'+set+' .key-group[data-cat="'+input.getAttribute("data-cat")+'"]'),label=input.parentNode;
   input.disabled=empty;label.classList.toggle("disabled",empty);
   if(empty)label.title=set==="main"?"only on the "+__RESCUE_SET_LABEL__:"only on the main ladder";
   else label.removeAttribute("title")
  })
 }
 w.querySelectorAll('.set-filter input').forEach(function(input){
  input.checked=input.value==="main";
  input.addEventListener("change",function(){if(input.checked){clear();w.classList.toggle("rescue",input.value==="rescue");updateCategories(input.value)}})
 });
 var toggle=w.querySelector('.cost-toggle input');
 if(toggle){toggle.checked=false;toggle.addEventListener("change",function(){clear();w.classList.toggle("free",toggle.checked)})}
 w.querySelectorAll('.category-filter input').forEach(function(input){
  input.checked=true;input.addEventListener("change",function(){clear();w.classList.toggle("hide-"+input.getAttribute("data-cat"),!input.checked);w.querySelectorAll("svg").forEach(refront)})
 });
 // Same rules as analysis/page.py front() and speed_dominates(), over the points still shown.
 function refront(svg){
  var path=svg.querySelector("path[data-front]");if(!path||!path.getAttribute("data-front"))return;
  var speed=path.getAttribute("data-front")==="speed",hidden=function(c){return w.classList.contains("hide-"+c)};
  var pts=[].map.call(svg.querySelectorAll(".pt"),function(g){var v=g.getAttribute("data-v").split(" ").map(Number),f=g.getAttribute("data-f").split(" ").map(Number);
   return {g:g,x:v[0],y:v[1],fx:f[0],fy:f[1]}}).filter(function(p){return !hidden(p.g.getAttribute("data-cat"))&&!p.g.hasAttribute("data-out")});
  function better(a,b){if(!speed)return a.x<=b.x&&a.y>=b.y;var t=Math.min(.5,b.x*.05);return a.y<b.y&&a.x<=b.x+t||a.y===b.y&&a.x<=b.x-t}
  var fr=pts.filter(function(p){return !pts.some(function(q){return q!==p&&better(q,p)&&(q.x!==p.x||q.y!==p.y)})}).sort(function(a,b){return a.x-b.x});
  var end=" H"+path.getAttribute("data-end"),d="";
  if(fr.length&&!speed)d="M"+fr[0].fx+" "+path.getAttribute("data-b")+" V"+fr[0].fy;
  else if(fr.length)d="M"+fr[0].fx+" "+fr[0].fy;
  if(d){fr.slice(1).forEach(function(p){d+=" H"+p.fx+" V"+p.fy});d+=end}
  path.setAttribute("d",d);
  var zone=svg.querySelector("path.zone");
  if(zone)zone.setAttribute("d",d?d+(speed?" V"+path.getAttribute("data-t")+" H"+fr[0].fx:" V"+path.getAttribute("data-b"))+" Z":"");
  svg.querySelectorAll(".ring").forEach(function(r){r.remove()});
  var on={};fr.forEach(function(p){on[p.g.getAttribute("data-c")]=1;
   var m=p.g.querySelector("circle:last-child"),r=document.createElementNS(svg.namespaceURI,"circle");
   [["class","ring"],["cx",m.getAttribute("cx")],["cy",m.getAttribute("cy")],["r",13],["fill","none"],["stroke","var(--frontier)"],["stroke-width",3]].forEach(function(a){r.setAttribute(a[0],a[1])});
   p.g.insertBefore(r,p.g.children[p.g.querySelector("line")?1:0])});
  var ranks=svg.querySelector(".ranks"),list=svg.parentNode.querySelector(".picks ol");
  if(ranks){ranks.textContent="";if(list)list.textContent="";
   fr.forEach(function(p,i){var m=p.g.querySelector("circle:last-child"),x=Math.min(+m.getAttribute("cx")+13,+path.getAttribute("data-end")-11),y=Math.max(+m.getAttribute("cy")-13,+path.getAttribute("data-t")+11),NS=svg.namespaceURI;
    var g=document.createElementNS(NS,"g"),c=document.createElementNS(NS,"circle"),t=document.createElementNS(NS,"text");
    g.setAttribute("class","rk");g.setAttribute("data-c",p.g.getAttribute("data-c"));
    [["cx",x],["cy",y],["r",10.5],["fill","var(--frontier)"],["stroke","var(--panel)"],["stroke-width",1.5]].forEach(function(a){c.setAttribute(a[0],a[1])});
    [["x",x],["y",y+4.5],["text-anchor","middle"],["class","rk-n"]].forEach(function(a){t.setAttribute(a[0],a[1])});
    t.textContent=i+1;g.appendChild(c);g.appendChild(t);ranks.appendChild(g);
    if(list){var key=svg.closest(".cvariant").querySelector('.ckey li[data-c="'+p.g.getAttribute("data-c")+'"][data-set="'+p.g.getAttribute("data-set")+'"]'),li=document.createElement("li");
     ["data-c","data-cat","data-set","data-tip"].forEach(function(a){li.setAttribute(a,p.g.getAttribute(a))});li.setAttribute("tabindex","0");
     var ic=key&&key.querySelector("svg");if(ic)li.appendChild(ic.cloneNode(true));
     var b=document.createElement("b");b.textContent=i+1;li.appendChild(b);
     var n=document.createElement("span");n.textContent=key?key.querySelector(".n").textContent:p.g.getAttribute("data-c");li.appendChild(n);list.appendChild(li);bind(li)}
   })}
  svg.querySelectorAll(".pt").forEach(function(g){if(on[g.getAttribute("data-c")])g.setAttribute("data-best","");else g.removeAttribute("data-best")});
  var v=svg.closest(".cvariant");if(v)v.querySelectorAll(".ckey li").forEach(function(li){li.classList.toggle("on",!!on[li.getAttribute("data-c")])})
 }
 updateCategories("main");
 function show(el,x,y){
  w.classList.add("hov");all().forEach(function(e){var m=e.getAttribute("data-c")===el.getAttribute("data-c")&&e.getAttribute("data-set")===el.getAttribute("data-set");e.classList.toggle("hi",m);e.classList.toggle("dim",!m)});
  tip.textContent=el.getAttribute("data-tip")||"";tip.hidden=false;
  var wr=w.getBoundingClientRect(),tw=tip.offsetWidth,th=tip.offsetHeight;
  var l=Math.max(0,Math.min(x-wr.left+12,wr.width-tw)),t=y-wr.top+14;
  if(t+th>wr.height)t=Math.max(0,y-wr.top-th-10);
  tip.style.left=l+"px";tip.style.top=t+"px"}
 function at(el,ev){if(ev&&ev.clientX!=null&&(ev.clientX||ev.clientY))show(el,ev.clientX,ev.clientY);else{var r=el.getBoundingClientRect();show(el,r.left+r.width/2,r.bottom)}}
 function bind(el){
  if(el.tagName==="g"){el.setAttribute("tabindex","0")}
  el.addEventListener("mouseenter",function(ev){at(el,ev)});
  el.addEventListener("mousemove",function(ev){at(el,ev)});
  el.addEventListener("mouseleave",clear);
  el.addEventListener("focus",function(){at(el,null)});
  el.addEventListener("blur",clear);
  el.addEventListener("click",function(ev){ev.stopPropagation();at(el,ev)});
 }
 all().forEach(bind);
 document.addEventListener("click",function(ev){if(!w.contains(ev.target)||ev.target===w)clear()});
 document.addEventListener("keydown",function(ev){if(ev.key==="Escape"){clear();if(document.activeElement&&w.contains(document.activeElement))document.activeElement.blur()}});
});})();

// Progressive section disclosure; stored choices yield to an explicit hash target.
(function(){
var storageKey="bench-report-collapsed-sections",collapsed=[],sections=[];
try{var saved=JSON.parse(localStorage.getItem(storageKey));if(Array.isArray(saved))collapsed=saved}catch(e){}
function uniqueId(base){
 var id=base,n=2;while(document.getElementById(id))id=base+"-"+n++;return id
}
function setOpen(item,open){
 item.body.hidden=!open;
 item.button.setAttribute("aria-expanded",String(open));
 item.chevron.textContent=open?"▾":"▸"
}
function persist(){
 try{localStorage.setItem(storageKey,JSON.stringify(sections.filter(function(item){return item.body.hidden}).map(function(item){return item.section.id})))}catch(e){}
}
function updateAll(){
 if(allButton)allButton.textContent=sections.some(function(item){return item.body.hidden})?"Expand all":"Collapse all"
}
document.querySelectorAll("main > section").forEach(function(section,i){
 var heading=section.querySelector("h1,h2,h3,h4,h5,h6");
 if(!heading||heading.tagName!=="H2"||section.classList.contains("collapsible"))return;
 if(!section.id)section.id=uniqueId("bench-section-"+(i+1));
 var button=document.createElement("button"),chevron=document.createElement("span"),body=document.createElement("div");
 button.type="button";button.className="sec-toggle";
 body.className="sec-body";body.id=uniqueId(section.id+"-body");
 button.setAttribute("aria-controls",body.id);
 while(heading.firstChild)button.appendChild(heading.firstChild);
 chevron.className="sec-chevron";chevron.setAttribute("aria-hidden","true");button.appendChild(chevron);
 heading.appendChild(button);
 if(heading.parentNode!==section)section.insertBefore(heading,section.firstChild);
 Array.prototype.slice.call(section.childNodes).forEach(function(node){if(node!==heading)body.appendChild(node)});
 section.appendChild(body);section.classList.add("collapsible");
 var item={section:section,button:button,chevron:chevron,body:body};sections.push(item);
 setOpen(item,collapsed.indexOf(section.id)===-1);
 button.addEventListener("click",function(){document.documentElement.classList.add("sec-anim");setOpen(item,body.hidden);updateAll();persist()})
});
if(!sections.length)return;
var toc=document.querySelector("main nav.toc"),allButton;
if(toc){
 allButton=document.createElement("button");allButton.type="button";allButton.className="sec-toggle-all";
 toc.insertAdjacentElement("afterend",allButton);
 allButton.addEventListener("click",function(){
  document.documentElement.classList.add("sec-anim");var open=sections.some(function(item){return item.body.hidden});
  sections.forEach(function(item){setOpen(item,open)});updateAll();persist()
 });
 toc.addEventListener("click",function(ev){
  var link=ev.target.closest("a[href]");
  if(!link||ev.defaultPrevented||ev.button!==0||ev.ctrlKey||ev.metaKey||ev.shiftKey||ev.altKey)return;
  if(link.getAttribute("href").charAt(0)==="#")revealHash(link.hash)
 })
}
function revealHash(hash){
 if(!hash||hash==="#")return;
 var id=hash.slice(1);try{id=decodeURIComponent(id)}catch(e){}
 var target=document.getElementById(id);if(!target)return;
 sections.forEach(function(item){if(item.section.contains(target))setOpen(item,true)});
 for(var d=target;d;d=d.parentElement)if(d.tagName==="DETAILS")d.open=true;
 updateAll();persist();target.scrollIntoView()
}
updateAll();revealHash(location.hash);
window.addEventListener("hashchange",function(){revealHash(location.hash)})
})();
// Wide tables scroll inside their box; fade the edge that hides columns, so a narrow screen shows there is more.
(function(){
function edge(w){var more=w.scrollWidth>w.clientWidth+2;w.classList.toggle("more-r",more&&w.scrollLeft+w.clientWidth<w.scrollWidth-2);w.classList.toggle("more-l",more&&w.scrollLeft>2)}
var ws=document.querySelectorAll(".tablewrap,.wrap,.svgscroll");
ws.forEach(function(w){w.addEventListener("scroll",function(){edge(w)},{passive:true})});
function all(){ws.forEach(edge)}
all();window.addEventListener("resize",all);document.addEventListener("toggle",all,true);
})();
