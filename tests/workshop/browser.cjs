// Runs inside the pinned Playwright container against isolated local apps.
const {chromium}=require('/tmp/browser/node_modules/playwright');
const fs=require('fs');
const assert=require('assert');
function env(slug){return Object.fromEntries(fs.readFileSync('/workspace/artifacts/workshop-check/apps/'+slug+'/.env','utf8').trim().split(/\r?\n/).filter(x=>x.includes('=')).map(x=>{const i=x.indexOf('=');return [x.slice(0,i),x.slice(i+1)];}));}
(async()=>{
 const browser=await chromium.launch({headless:true});
 const context=await browser.newContext();const page=await context.newPage();
 const a=env('workshop-check-a'),b=env('workshop-check-b');
 const baseA='http://host.docker.internal:'+a.APP_PORT,baseB='http://host.docker.internal:'+b.APP_PORT;
 // Use the external browser-test origin explicitly; normal app origins remain
 // localhost. Requests route to host loopback through the container gateway.
 for(const size of [{width:1440,height:900},{width:390,height:844}]){
  await page.setViewportSize(size);await page.goto(baseA);await page.getByLabel('Email').waitFor();
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
 }
 await page.route('**/api/**',async route=>{
  const h={...route.request().headers()};if(h.origin)h.origin=a.APP_ORIGIN;
  await route.continue({headers:h});
 });
 await page.getByLabel('Email').fill(a.ADMIN_EMAIL);await page.getByLabel('Password').fill(a.ADMIN_PASSWORD);
 await page.getByRole('button',{name:'Sign in',exact:true}).click();
 await page.getByLabel('New note').waitFor();
 if(await page.getByText('No notes yet. Add your first note when ready.').isVisible()){
  await page.getByLabel('New note').fill('Isolated workshop persistence check');await page.getByRole('button',{name:'Save note'}).click();
 }
 await page.getByText('Isolated workshop persistence check',{exact:true}).waitFor();
 await page.screenshot({path:'/workspace/artifacts/workshop-check/starter-mobile.png',fullPage:true});
 // Same hostname, different ports: distinct names prevent cross-app auth.
 await page.goto(baseB);await page.getByLabel('Email').waitFor();
 await page.goto(baseA);await page.getByText('Isolated workshop persistence check',{exact:true}).waitFor();
 await page.getByRole('button',{name:'Sign out'}).click();await page.getByLabel('Email').waitFor();
 console.log('Browser: sign-in, desktop/mobile fit, persisted note, cookie separation, reload and sign-out PASS');
 await browser.close();
})().catch(e=>{console.error(e.message);process.exit(1);});
