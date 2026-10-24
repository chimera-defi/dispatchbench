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
 var tip=w.querySelector(".ctip"),all=w.querySelectorAll(".pt,.ckey li");
 function clear(){w.classList.remove("hov");all.forEach(function(e){e.classList.remove("hi","dim")});tip.hidden=true}
 function show(el,x,y){
  w.classList.add("hov");all.forEach(function(e){var m=e.getAttribute("data-c")===el.getAttribute("data-c");e.classList.toggle("hi",m);e.classList.toggle("dim",!m)});
  tip.textContent=el.getAttribute("data-tip")||"";tip.hidden=false;
  var wr=w.getBoundingClientRect(),tw=tip.offsetWidth,th=tip.offsetHeight;
  var l=Math.max(0,Math.min(x-wr.left+12,wr.width-tw)),t=y-wr.top+14;
  if(t+th>wr.height)t=Math.max(0,y-wr.top-th-10);
  tip.style.left=l+"px";tip.style.top=t+"px"}
 function at(el,ev){if(ev&&ev.clientX!=null&&(ev.clientX||ev.clientY))show(el,ev.clientX,ev.clientY);else{var r=el.getBoundingClientRect();show(el,r.left+r.width/2,r.bottom)}}
 all.forEach(function(el){
  if(el.tagName==="g"){el.setAttribute("tabindex","0")}
  el.addEventListener("mouseenter",function(ev){at(el,ev)});
  el.addEventListener("mousemove",function(ev){at(el,ev)});
  el.addEventListener("mouseleave",clear);
  el.addEventListener("focus",function(){at(el,null)});
  el.addEventListener("blur",clear);
  el.addEventListener("click",function(ev){ev.stopPropagation();at(el,ev)});
 });
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
 updateAll();persist();target.scrollIntoView()
}
updateAll();revealHash(location.hash);
window.addEventListener("hashchange",function(){revealHash(location.hash)})
})();
