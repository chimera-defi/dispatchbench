// Activate a column header button to sort its table; activate again to reverse. Numbers sort as numbers ("95% (57/60)" sorts by 95,
// "$0.00112" by 0.00112, "1,569" by 1569); a column whose cells are not numbers sorts as text; "–" goes last either way.
// Each tbody sorts on its own, under its "grp" heading row, so the all-problems and hard-set groups never mix.
(function(){
// A cell is numeric only when it starts with a number (after ≥, ~, $ or a sign), so "sol61-medium" sorts as text.
function key(td){var t=td.textContent.replace(/,/g,"").replace(/−/g,"-").trim();var m=t.match(/^[≥≤~]?\$?([+-]?\d+(\.\d+)?)/);return m?parseFloat(m[1]):null}
document.querySelectorAll("table.sortable").forEach(function(tb){
 var ths=tb.tHead.rows[0].cells;
 Array.prototype.forEach.call(ths,function(th,i){
  var button=document.createElement("button");button.type="button";button.className="sort-btn";button.title="Sort by this column";
  while(th.firstChild)button.appendChild(th.firstChild);
  th.appendChild(button);th.setAttribute("aria-sort","none");button.onclick=function(){
  var desc=th.getAttribute("aria-sort")==="ascending";Array.prototype.forEach.call(ths,function(h){h.setAttribute("aria-sort","none")});
  th.setAttribute("aria-sort",desc?"descending":"ascending");
  Array.prototype.forEach.call(tb.tBodies,function(body){
  var rows=Array.prototype.filter.call(body.rows,function(r){return !r.classList.contains("grp")});
  rows.sort(function(a,b){var x=key(a.cells[i]),y=key(b.cells[i]);
   var ta=a.cells[i].textContent.trim(),tb2=b.cells[i].textContent.trim();
   if(ta==="–"||tb2==="–")return ta===tb2?0:ta==="–"?1:-1;
   if(x===null||y===null){var s=ta.localeCompare(tb2);return desc?-s:s}
   return desc?y-x:x-y});
  rows.forEach(function(r){body.appendChild(r)})})}})})})();
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
 var permalink=heading.querySelector(".hlink");
 Array.prototype.slice.call(heading.childNodes).forEach(function(node){if(node!==permalink)button.appendChild(node)});
 chevron.className="sec-chevron";chevron.setAttribute("aria-hidden","true");button.appendChild(chevron);
 heading.insertBefore(button,permalink);
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
 var explorer=document.getElementById('pareto-explorer');
 if(id.indexOf('config-')===0&&explorer&&explorer.resolveConfigHash)explorer.resolveConfigHash(id);
 var target=document.getElementById(id);if(!target)return;
 sections.forEach(function(item){if(item.section.contains(target))setOpen(item,true)});
 for(var d=target;d;d=d.parentElement)if(d.tagName==="DETAILS")d.open=true;
 var row=target.closest(".prow");if(row){var statement=row.querySelector(".problem-try");if(statement)statement.open=true}
 updateAll();persist();target.scrollIntoView({block:"start"})
}
function anchorOffset(){
 var bar=document.querySelector(".ds-topbar");
 document.documentElement.style.setProperty("--anchor-offset",((bar?bar.getBoundingClientRect().height:0)+16)+"px")
}
anchorOffset();window.addEventListener("resize",anchorOffset);
updateAll();revealHash(location.hash);
window.addEventListener("hashchange",function(){revealHash(location.hash)})
window.addEventListener("load",function(){revealHash(location.hash)});
// Preserve native navigation (including keyboard activation). Copying is optional.
var status=document.querySelector(".link-status"),statusTimer;
document.addEventListener("click",function(ev){
 var link=ev.target.closest("a.hlink");
 if(!link||ev.defaultPrevented||ev.button!==0||ev.ctrlKey||ev.metaKey||ev.shiftKey||ev.altKey)return;
 revealHash(link.hash);
 if(!navigator.clipboard||!navigator.clipboard.writeText)return;
 try{Promise.resolve(navigator.clipboard.writeText(link.href)).then(function(){
  if(!status)return;
  clearTimeout(statusTimer);status.textContent="Link copied";
  statusTimer=setTimeout(function(){status.textContent=""},1800)
 }).catch(function(){})}catch(e){}
});
})();
// Wide tables scroll inside their box; fade the edge that hides columns, so a narrow screen shows there is more.
(function(){
function edge(w){var more=w.scrollWidth>w.clientWidth+2;w.classList.toggle("more-r",more&&w.scrollLeft+w.clientWidth<w.scrollWidth-2);w.classList.toggle("more-l",more&&w.scrollLeft>2)}
var ws=document.querySelectorAll(".tablewrap,.wrap,.svgscroll");
ws.forEach(function(w){w.addEventListener("scroll",function(){edge(w)},{passive:true})});
function all(){ws.forEach(edge)}
all();window.addEventListener("resize",all);document.addEventListener("toggle",all,true);
})();
