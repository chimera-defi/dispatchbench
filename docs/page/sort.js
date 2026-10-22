// Click a column header to sort its table; click again to reverse. Numbers sort as numbers ("95% (57/60)" sorts by 95,
// "$0.00112" by 0.00112, "1,569" by 1569); a column whose cells are not numbers sorts as text; "–" goes last either way.
(function(){
// A cell is numeric only when it starts with a number (after ≥, $ or a sign), so "sol61-medium" sorts as text.
function key(td){var t=td.textContent.replace(/,/g,"").replace(/−/g,"-").trim();var m=t.match(/^[≥≤]?\$?([+-]?\d+(\.\d+)?)/);return m?parseFloat(m[1]):null}
document.querySelectorAll("table.sortable").forEach(function(tb){
 var ths=tb.tHead.rows[0].cells;
 Array.prototype.forEach.call(ths,function(th,i){th.title="Sort by this column";th.onclick=function(){
  var desc=th.getAttribute("aria-sort")==="ascending";Array.prototype.forEach.call(ths,function(h){h.removeAttribute("aria-sort")});
  th.setAttribute("aria-sort",desc?"descending":"ascending");
  var rows=Array.prototype.slice.call(tb.tBodies[0].rows);
  rows.sort(function(a,b){var x=key(a.cells[i]),y=key(b.cells[i]);
   var ta=a.cells[i].textContent.trim(),tb2=b.cells[i].textContent.trim();
   if(ta==="–"||tb2==="–")return ta===tb2?0:ta==="–"?1:-1;
   if(x===null||y===null){var s=ta.localeCompare(tb2);return desc?-s:s}
   return desc?y-x:x-y});
  rows.forEach(function(r){tb.tBodies[0].appendChild(r)})}})})})();
