import {test,expect} from '@playwright/test';
import fs from 'node:fs';

test('live showcase: read-only screens, filters, role actions and Finance preview',async({page})=>{
 test.skip(process.env.SHOWCASE_LIVE!=='true','Runs only for an explicitly imported live showcase');
 const env=Object.fromEntries(fs.readFileSync('/config/.env','utf8').split(/\r?\n/).filter(l=>l.includes('=')).map(l=>{const n=l.indexOf('=');return [l.slice(0,n),l.slice(n+1)];}));
 const report=JSON.parse(fs.readFileSync('/config/local/harborworks-verification.json','utf8'));
 const credentials=JSON.parse(fs.readFileSync('/config/local/harborworks-demo-v1-credentials.json','utf8'));
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',route=>new URL(route.request().url()).origin==='http://frontend'?route.continue():route.abort());
 async function login(email:string,password:string){await page.goto('/');await page.getByLabel('Email',{exact:true}).fill(email);await page.getByLabel('Password',{exact:true}).fill(password);await page.getByRole('button',{name:'Sign in →',exact:true}).click();await expect(page.locator('.loading')).toHaveCount(0);await expect(page.getByRole('heading',{name:'A clearer path from idea to impact'})).toBeVisible();}
 async function logout(){const csrf=(await (await page.request.get('/api/v1/session/me')).json()).csrf;expect((await page.request.post('/api/v1/session/logout',{headers:{'X-CSRF-Token':csrf}})).ok()).toBeTruthy();}
 await login(env.ADMIN_EMAIL,env.ADMIN_PASSWORD);
 const total=(await (await page.request.get('/api/v1/ideas?page_size=100')).json()).total;expect(total).toBeGreaterThanOrEqual(60);
 for(const width of [1440,1280,390]){
   await page.setViewportSize({width,height:width===1440?900:width===1280?720:844});
   for(const [path,name] of [['/','overview'],['/ideas','register'],['/pipeline','pipeline'],['/process','process'],['/value','value'],['/ideas/'+report.heroes[0].id+'?tab=financials','financials']]){
     await page.goto(path);await expect(page.locator('h1')).toBeVisible();await expect(page.locator('.loading')).toHaveCount(0);await page.waitForTimeout(500);
     expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),name+' overflow at '+width).toBe(false);
     if(name==='register')await expect(page.getByText(total+' ideas in this view')).toBeVisible();
     if(name==='process'){await expect(page.locator('.react-flow__node').first()).toBeVisible();if(width!==390){await page.locator('.process-graph').screenshot({path:`/artifacts/showcase-graph-${width}.png`});await page.locator('.process-graph').evaluate((e:HTMLElement)=>{e.scrollLeft=e.scrollWidth;});await page.locator('.process-graph').screenshot({path:`/artifacts/showcase-graph-${width}-right.png`});}}
     await page.screenshot({path:`/artifacts/showcase-${name}-${width}.png`});
   }
 }
 await page.setViewportSize({width:1440,height:900});
 const tampa=(await (await page.request.get('/api/v1/ideas?site_id=Tampa')).json()).total;await page.goto('/ideas?site_id=Tampa');await expect(page.getByLabel('Location',{exact:true})).toHaveValue('Tampa');await page.reload();await expect(page.getByText(tampa+' ideas in this view')).toBeVisible();
 await page.goto('/process');await expect(page.locator('.loading')).toHaveCount(0);await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page).toHaveURL(/ids=/);await expect(page.getByText('Showing contributing ideas from analytics. Reset to see the full register.')).toBeVisible();
 for(const hero of report.heroes){await page.goto('/ideas/'+hero.id);await expect(page.getByRole('heading',{name:hero.title,exact:true})).toBeVisible();await expect(page.getByText('Fictional demo data',{exact:true})).toBeVisible();await page.getByRole('tab',{name:'History',exact:true}).click();await expect(page.getByText(new RegExp('Fictional demo data · harborworks-demo-v1')).first()).toBeVisible();}
 await page.goto('/ideas/new');await page.getByLabel('Idea title',{exact:true}).fill('Reduce repeat checks at the dispatch handoff');await page.getByLabel('Problem / opportunity').fill('Two teams check the same order and delay release');await page.getByLabel('Proposed improvement').fill('Agree one checklist and one owner');await page.getByLabel('Location (optional)',{exact:true}).fill('Tampa');await page.getByLabel('Category (optional)',{exact:true}).fill('Freight');await expect(page.getByRole('button',{name:'Create idea',exact:true})).toBeEnabled();
 // The form preview is intentionally left unsaved for the presenter to create live.
 await logout();const manager=credentials.find((c:any)=>c.role==='Manager');await login(manager.email,manager.password);await page.goto('/ideas/'+report.heroes[2].id);await expect(page.getByRole('button',{name:'Move to Approved →',exact:true})).toBeVisible();await expect(page.getByLabel('Owner',{exact:true})).toBeEnabled();await logout();
 const finance=credentials.find((c:any)=>c.role==='Finance');await login(finance.email,finance.password);await page.goto('/ideas/'+report.heroes[3].id+'?tab=financials');const month=report.heroes[3].results.find((r:any)=>!r.verified_at&&r.gross!==null).month;await page.getByLabel('Outcome month').fill(month.slice(0,7));await page.getByRole('button',{name:'Review result verification'}).click();await expect(page.getByRole('dialog',{name:'Result review'})).toBeVisible();await expect(page.getByLabel('Reviewed gross (USD)')).not.toHaveValue('');await page.getByLabel('Verification reason').fill('Reviewed pilot measurement against the agreed baseline');await expect(page.getByRole('button',{name:'Confirm result verification'})).toBeEnabled();await page.getByRole('dialog').screenshot({path:'/artifacts/showcase-finance-preview.png'});await page.getByRole('button',{name:'Close dialog',exact:true}).click();
 const detail=await (await page.request.get('/api/v1/ideas/'+report.heroes[3].id)).json();expect(detail.results.find((r:any)=>r.month===month).verified_at).toBeNull();expect(errors).toEqual([]);
});
