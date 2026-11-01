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
   await page.goto(base+'#p07');await visibleTarget('p07');
   assert(await page.locator('#p07-try').evaluate(el=>el.open),'row hash opens Try it');
   assert.equal(await page.locator('#p08-try').evaluate(el=>el.open),false,'other statements stay closed');
   await page.goto(base+'#method-models-and-versions');await visibleTarget('method-models-and-versions');
   await page.goto(base+'#key-numbers');await visibleTarget('key-numbers');
   // Reach a hidden permalink by keyboard; Tab must reveal its focus indicator.
   await page.goto(base+'#problems');
   const link=page.locator('a.hlink[href="#problems-try-them-yourself"]');
   await page.locator('#problems > h2 > button').focus();await page.keyboard.press('Tab');
   assert(await link.evaluate(el=>el===document.activeElement&&el.matches(':focus-visible')));
   assert.equal(await link.evaluate(el=>getComputedStyle(el).opacity),'1');
   assert.equal(await link.evaluate(el=>!!el.closest('button')),false,'link must not be nested in disclosure button');
   // Clipboard success, silent rejection and missing API all preserve native hash navigation.
   await page.evaluate(()=>{window.copiedLinks=[];Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>window.copiedLinks.push(text)}})});
   await link.press('Enter');await visibleTarget('problems-try-them-yourself');
   assert.equal(await page.evaluate(()=>location.hash),'#problems-try-them-yourself');
   assert.deepEqual(await page.evaluate(()=>window.copiedLinks),[base+'#problems-try-them-yourself']);
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
  console.log('deep links: p07, method disclosure, existing nested hash, keyboard focus, clipboard success/failure/unavailable, touch and 390px overflow pass');
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
