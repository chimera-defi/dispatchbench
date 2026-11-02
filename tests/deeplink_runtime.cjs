// R6: exercise actual shipped HTML and navigation in Chrome, without remote scripts.
const path=require('path'),assert=require('assert');
const {pathToFileURL}=require('url');
const {chromium}=require('playwright');
(async()=>{
 const base=pathToFileURL(path.resolve('results/report/page.html')).href;
 const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 try{
  for(const width of [1280,390]){
   const context=await browser.newContext({viewport:{width,height:900}});
   await context.route('**/*',route=>route.request().url().startsWith(base)?route.continue():route.abort());
   await context.addInitScript(()=>localStorage.setItem('bench-report-collapsed-sections',JSON.stringify(['problems','method','grok'])));
   const page=await context.newPage();
   const errors=[];page.on('pageerror',error=>errors.push(error.message));
   const visibleTarget=async(id)=>{
    await page.waitForFunction(id=>{
     const el=document.getElementById(id);if(!el)return false;
     const r=el.getBoundingClientRect();return r.top>=0&&r.top<innerHeight;
    },id);
    const result=await page.locator(`[id="${id}"]`).evaluate(el=>{
     const r=el.getBoundingClientRect(),bar=document.querySelector('.ds-topbar').getBoundingClientRect();
     return {top:r.top,bottom:r.bottom,barBottom:Math.max(0,bar.bottom),hidden:!!el.closest('[hidden]'),
      closed:Array.from(document.querySelectorAll('details')).some(d=>d.contains(el)&&!d.open)};
    });
    assert(!result.hidden&&!result.closed,`${width}/${id} hidden: ${JSON.stringify(result)}`);
    assert(result.top>=result.barBottom&&result.top<900,`${width}/${id} under bar or outside viewport`);
   };
   // R8: navigate from a new document, rather than a previously selected card.
   for(const [id,set] of [['config-sonnet-medium','main'],['config-sonnet-low','pilot']]){
    await page.goto(base+'?fresh='+id+'#'+id);await visibleTarget(id);
    assert.equal(await page.locator('#ex-set').inputValue(),set);
    assert.equal(await page.locator('#ex-detail h3').getAttribute('id'),id);
   }
   await page.evaluate(()=>{location.hash='config-sonnet-medium'});await visibleTarget('config-sonnet-medium');
   assert.equal(await page.locator('#ex-set').inputValue(),'main');
   await page.evaluate(()=>{location.hash='config-sonnet-low'});await visibleTarget('config-sonnet-low');
   assert.equal(await page.locator('#ex-set').inputValue(),'pilot');
   await page.locator('#ex-chart .ex-point').first().focus();
   await page.evaluate(()=>{location.hash='config-sonnet-medium'});await visibleTarget('config-sonnet-medium');
   assert.equal(await page.locator('#ex-detail h3').getAttribute('id'),'config-sonnet-medium','old point focus must yield to explicit hash selection');
   await page.evaluate(()=>{location.hash='config-sonnet-low'});await visibleTarget('config-sonnet-low');
   // Every retained heading has a stable permalink.
   const headingSnapshot=async()=>page.locator('main h2,main h3').evaluateAll(headings=>headings.map(h=>({
    id:h.id,text:h.textContent,section:h.closest('section')?.querySelector('h1,h2,h3,h4,h5,h6')===h?h.closest('section').id:null,
    links:Array.from(h.querySelectorAll('a.hlink'),a=>({href:a.getAttribute('href'),label:a.getAttribute('aria-label'),text:a.textContent,tab:a.getAttribute('tabindex')}))
   })));
   const headings=await headingSnapshot();assert(headings.length>0);
   for(const h of headings){
    if(h.section){
     assert.equal(h.id,h.section==='grok'?'grok-and-devin':'',`${width}/${h.section} title must use the section target`);
     assert(!/-\d+$/.test(h.id));
    }else assert(/^[a-z][a-z0-9_-]*$/.test(h.id),`${width} heading lacks a valid id: ${h.text}`);
    assert.equal(h.links.length,1,`${width}/${h.id} missing/duplicate permalink`);
    assert.equal(h.links[0].href,'#'+(h.section||h.id));assert.equal(h.links[0].text,'#');
    assert(h.links[0].label.startsWith('Link to this section: '));assert.notEqual(h.links[0].tab,'-1');
   }
   const grokIds=await page.locator('#grok h2,#grok h3').evaluateAll(hs=>hs.map(h=>h.id));
   assert.deepEqual(grokIds,['grok-and-devin']);
   const ids=await page.locator('[id]').evaluateAll(els=>els.map(el=>el.id));assert.equal(new Set(ids).size,ids.length,'live ids must not collide');
   assert(!ids.some(id=>id.includes('accuracyone')),'heading words must not glue together');
   for(const id of ['results','pareto','grok']){
    await page.goto(base+'?fresh=section-'+id+'#'+id);await visibleTarget(id);
    const position=await page.locator('#'+id+' > h2').evaluate(h=>({top:h.getBoundingClientRect().top,bar:Math.max(0,document.querySelector('.ds-topbar').getBoundingClientRect().bottom)}));
    assert(position.top>=position.bar&&position.top<900,`${width}/${id} heading under bar or outside viewport`);
   }
   await page.goto(base+'#config-sonnet-low');await visibleTarget('config-sonnet-low');
   assert(await page.locator('[aria-live="polite"]').count()>0);
   await page.reload();await visibleTarget('config-sonnet-low');
   assert.deepEqual(await headingSnapshot(),headings,'live heading slugs and controls are deterministic');
   await page.goto(base+'#'+grokIds[0]);await visibleTarget(grokIds[0]);
   // The historical speed URL selects the preset inside the one any-pair figure.
   await page.goto(base+'?fresh=speed#speed-vs-per-pass');await visibleTarget('xfig');
   assert.equal(await page.locator('#pair-speed-preset').getAttribute('aria-pressed'),'true');
   assert(await page.locator('#pair-speed').isVisible());assert(!(await page.locator('#pair-custom').isVisible()));
   assert.equal(await page.locator('#pair-speed svg[role="img"]').count(),4);
   const wrap=page.locator('#pair-speed .cwrap');
   assert(await wrap.locator('.s-main .v-normal .cplot').isVisible());
   assert(!(await wrap.locator('.s-main .v-free .cplot').isVisible()));
   await wrap.locator('.set-filter input[value="rescue"]').check();
   await wrap.locator('.cost-toggle input').check();
   assert(await wrap.locator('.s-rescue .v-free .cplot').isVisible());
   assert(!(await wrap.locator('.s-main .v-free .cplot').isVisible()));
   const speedSvg=wrap.locator('.s-rescue .v-free .cplot > svg');
   assert(await speedSvg.locator('.ring').count()>0);assert(await speedSvg.locator('.rk-n').count()>0);
   await wrap.locator('.category-filter input[data-cat="pipelines"]').uncheck();
   const frontierIds=await speedSvg.locator('.rk').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('data-c')));
   assert(frontierIds.length>0);assert(frontierIds.every(id=>!id.includes('+')),'filtered pipelines leave the frontier');
   assert.equal(await speedSvg.locator('.pt[data-cat="pipelines"]').first().isVisible(),false);
   await speedSvg.locator('.pt:visible').first().focus();
   assert(await wrap.locator('.ctip').isVisible(),'restored chart focus opens tooltip');
   await page.locator('#pair-custom-preset').click();
   assert(!(await page.locator('#pair-speed').isVisible()));assert(await page.locator('#pair-custom').isVisible());
   await page.evaluate(()=>{location.hash='xfig'});await visibleTarget('xfig');
   await page.evaluate(()=>{location.hash='speed-vs-per-pass'});await visibleTarget('xfig');
   assert.equal(await page.locator('#pair-speed-preset').getAttribute('aria-pressed'),'true');
   await page.evaluate(()=>{window.copiedLinks=[];Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>window.copiedLinks.push(text)}})});
   const speedLink=page.locator('a.hlink[href="#speed-vs-per-pass"]');
   assert.equal(await speedLink.evaluate(el=>getComputedStyle(el).opacity),'1');
   await speedLink.click();await visibleTarget('xfig');
   assert.deepEqual(await page.evaluate(()=>window.copiedLinks),[base+'?fresh=speed#speed-vs-per-pass']);
   // Exercise the actual generated point groups and event handlers, not a DOM stub.
   await page.goto(base+'#xfig');await visibleTarget('xfig');
   await page.waitForFunction(()=>document.querySelectorAll('#xplot .explorer-point').length>0);
   // Late web fonts resize the plot and its debounced redraw replaces the points; let it settle first.
   await page.evaluate(()=>document.fonts.ready);
   await page.waitForFunction(()=>new Promise(r=>{const s=document.querySelector('#xplot svg');setTimeout(()=>r(s&&s===document.querySelector('#xplot svg')),250)}));
   const point=page.locator('#xplot .explorer-point').first(),tip=page.locator('#pair-tip');
   assert.equal(await point.getAttribute('tabindex'),'0');assert.equal(await point.getAttribute('role'),'button');
   const name=await point.locator('title').textContent();
   const actionLabel=await point.getAttribute('aria-label');assert(actionLabel.includes(name)&&/inspect/i.test(actionLabel));
   await page.locator('#pair-cf input').last().focus();await page.keyboard.press('Tab');
   assert(await point.evaluate(el=>el===document.activeElement),'Tab reaches the first plotted point');
   assert(await tip.isVisible(),'focus opens inspector');
   for(const key of ['Enter','Space']){
    await point.press('Escape');assert.equal(await tip.isVisible(),false,'Escape dismisses inspector');
    const before=await page.evaluate(()=>scrollY);
    await point.press(key);assert(await tip.isVisible(),`${key} opens inspector`);
    assert.equal(await page.evaluate(()=>scrollY),before,`${key} must not scroll`);
    const text=await tip.textContent();assert(text.includes(name)&&text.includes('input tokens per call')&&text.includes('reasoning tokens per call'));
   }
   // A resize redraw replaces the SVG; keyboard focus and the open inspector must follow the same config.
   const di=await point.getAttribute('data-i');await point.press('Enter');
   const vp=page.viewportSize();const oldSvg=await page.evaluateHandle(()=>document.querySelector('#xplot svg'));
   await page.setViewportSize({width:vp.width-24,height:vp.height});
   await page.waitForFunction(old=>document.querySelector('#xplot svg')!==old,oldSvg);
   assert.equal(await page.evaluate(()=>document.activeElement&&document.activeElement.getAttribute('data-i')),di,'redraw keeps focus');
   assert(await tip.isVisible(),'redraw keeps inspector open');
   await page.setViewportSize(vp);await page.waitForTimeout(200);await point.focus();
   await point.press('Escape');assert.equal(await tip.isVisible(),false);
   await page.goto(base+'?fresh=problem#p07');await visibleTarget('p07');
   assert(await page.locator('#p07-try').evaluate(el=>el.open),'row hash opens Try it');
   assert.equal(await page.locator('#p08-try').evaluate(el=>el.open),false,'other statements stay closed');
   await page.goto(base+'#method-models-and-versions');await visibleTarget('method-models-and-versions');
   // Reach a hidden permalink by keyboard; Tab must reveal its focus indicator.
   await page.goto(base+'#problems');
   const link=page.locator('#problems > h2 > a.hlink[href="#problems"]');
   await page.locator('#problems > h2 > button').focus();await page.keyboard.press('Tab');
   assert(await link.evaluate(el=>el===document.activeElement&&el.matches(':focus-visible')));
   assert.equal(await link.evaluate(el=>getComputedStyle(el).opacity),'1');
   assert.equal(await link.evaluate(el=>!!el.closest('button')),false,'link must not be nested in disclosure button');
   // Clipboard success, silent rejection and missing API all preserve native hash navigation.
   await page.evaluate(()=>{window.copiedLinks=[];Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>window.copiedLinks.push(text)}})});
   await link.press('Enter');await visibleTarget('problems');
   assert.equal(await page.evaluate(()=>location.hash),'#problems');
   assert.deepEqual(await page.evaluate(()=>window.copiedLinks),[base+'#problems']);
   await page.waitForFunction(()=>document.querySelector('.link-status').textContent==='Link copied');
   assert(await page.locator('#problems > h2 > button').getAttribute('aria-expanded')==='true');
   await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw Error('denied')}}}));
   await page.locator('a.hlink[href="#p07"]').click();await visibleTarget('p07');
   await page.waitForFunction(()=>!document.querySelector('.link-status').textContent);
   await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined}));
   await page.locator('a.hlink[href="#p08"]').click();await visibleTarget('p08');
   assert.equal(await page.evaluate(()=>location.hash),'#p08');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`${width} horizontal overflow`);
   assert.deepEqual(errors,[]);
   await context.close();
  }
  const touch=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true});
  await touch.route('**/*',route=>route.request().url().startsWith(base)?route.continue():route.abort());
  const page=await touch.newPage();await page.goto(base+'#problems');
  assert.equal(await page.locator('a.hlink[href="#p07"]').evaluate(el=>getComputedStyle(el).opacity),'1','touch links always visible');
  await touch.close();
  console.log('deep links: fresh config and cross-set hashes, all headings including Grok, any-pair keyboard, p07, method disclosure, existing nested hash, keyboard focus, clipboard success/failure/unavailable, touch and 390px overflow pass');
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
