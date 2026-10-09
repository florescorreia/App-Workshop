import {test,expect} from '@playwright/test';
import fs from 'node:fs';
const env=Object.fromEntries(fs.readFileSync('/config/.env','utf8').split(/\r?\n/).filter(l=>l.includes('=')).map(l=>{const p=l.indexOf('=');return [l.slice(0,p),l.slice(p+1)];}));
async function login(page:any){await page.goto('/');await page.getByLabel('Email',{exact:true}).fill(env.ADMIN_EMAIL);await page.getByLabel('Password',{exact:true}).fill(env.ADMIN_PASSWORD);await page.getByRole('button',{name:'Sign in →',exact:true}).click();await expect(page.getByRole('heading',{name:'A clearer path from idea to impact'})).toBeVisible();}
test('empty startup remains usable, all navigation and nested refresh',async({page})=>{
 test.skip(process.env.VERIFY_DEMO==='true','Empty-only check targets live workspace');
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));await login(page);
 await expect(page.getByText('0 ideas in this view')).not.toBeVisible();
 for(const [path,title] of [['/ideas','Idea register'],['/pipeline','Move good ideas forward'],['/process','See how work actually flows'],['/value','Value, supported by evidence'],['/my-work','My Work'],['/settings','Workspace settings']]){await page.goto(path);await expect(page.getByRole('heading',{name:title,exact:true})).toBeVisible();await page.reload();await expect(page.getByRole('heading',{name:title,exact:true})).toBeVisible();}
 const response=await page.request.get('/api/v1/ideas');expect((await response.json()).total).toBe(0);expect(errors).toEqual([]);
 await page.route('**/*',route=>new URL(route.request().url()).origin===new URL(page.url()).origin?route.continue():route.abort());
 await page.goto('/api/docs');await expect(page.locator('.swagger-ui .info .title')).toContainText('IdeaFlow');expect(errors).toEqual([]);
});
test('layouts, observed graph, filters and detail financials',async({page})=>{
 test.skip(process.env.VERIFY_DEMO!=='true','Demo browser check uses isolated workspace');
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));await login(page);
 const response=await page.request.get('/api/v1/ideas?page_size=100');const data=await response.json();expect(data.total).toBeGreaterThanOrEqual(60);
 const hero=data.items.find((i:any)=>i.title==='Consolidate outbound freight into scheduled routes');expect(hero).toBeTruthy();
 for(const size of [{width:1440,height:900},{width:1280,height:720},{width:390,height:844}]){
   await page.setViewportSize(size);
   for(const [path,name] of [['/','overview'],['/ideas','register'],['/ideas/'+hero.id+'?tab=financials','financials'],['/pipeline','pipeline'],['/process','process'],['/value','value']]){
     await page.goto(path);await expect(page.locator('h1')).toBeVisible();await expect(page.locator('.loading')).toHaveCount(0);await page.waitForTimeout(700);
     if(name==='process'){await expect(page.locator('.react-flow__node').first()).toBeVisible();if(size.width!==390){await page.locator('.process-graph').screenshot({path:`/artifacts/graph-${size.width}.png`});await page.locator('.graph-canvas').screenshot({path:`/artifacts/graph-${size.width}-full.png`});await page.locator('.process-graph').evaluate((e:HTMLElement)=>{e.scrollLeft=e.scrollWidth;});await page.locator('.process-graph').screenshot({path:`/artifacts/graph-${size.width}-right.png`});await page.locator('.process-graph').evaluate((e:HTMLElement)=>{e.scrollLeft=0;});}}
     const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+2);expect(overflow,`${name} at ${size.width}`).toBe(false);
     await page.screenshot({path:`/artifacts/${name}-${size.width}.png`,fullPage:false});
     if(size.width!==390&&['process','financials','value'].includes(name))await page.screenshot({path:`/artifacts/${name}-${size.width}-full.png`,fullPage:true});
   }
 }
 await page.goto('/');await expect(page.locator('.loading')).toHaveCount(0);await page.getByLabel('From month',{exact:true}).fill('2026-01');await page.getByLabel('Through month',{exact:true}).fill('2026-06');await expect(page).toHaveURL(/end=2026-06-01/);await expect(page.locator('.loading')).toHaveCount(0);await page.getByRole('link',{name:/Active ideas/}).click();await expect(page).toHaveURL(/ids=/);await expect(page.getByText('Showing contributing ideas from analytics. Reset to see the full register.')).toBeVisible();
 await page.setViewportSize({width:1440,height:900});await page.goto('/ideas?site_id=Tampa');await expect(page.getByLabel('Location',{exact:true})).toHaveValue('Tampa');await page.reload();await expect(page.getByLabel('Location',{exact:true})).toHaveValue('Tampa');
 await page.goto('/process');await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page).toHaveURL(/ids=/);await expect(page.getByText('Showing contributing ideas from analytics. Reset to see the full register.')).toBeVisible();
 expect(errors).toEqual([]);
});
test('browser create, failed edit preservation, transition, comments and tasks',async({page})=>{
 test.skip(process.env.VERIFY_DEMO!=='true','Mutating browser check uses isolated workspace');
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));await login(page);await page.goto('/ideas/new');
 const title='Browser acceptance '+Date.now();await page.getByLabel('Idea title',{exact:true}).fill(title);await page.getByLabel('Problem / opportunity').fill('Repeated dispatch checks delay the handoff.');await page.getByLabel('Proposed improvement').fill('Use a single documented dispatch checklist.');await page.getByLabel('Location (optional)',{exact:true}).fill('Tampa');await page.getByLabel('Category (optional)',{exact:true}).fill('Freight');await page.getByRole('button',{name:'Create idea',exact:true}).click();await expect(page.getByRole('heading',{name:title,exact:true})).toBeVisible();
 await page.getByLabel('Screening note',{exact:true}).fill('Sponsor and baseline confirmed.');await page.getByRole('button',{name:'Save business case'}).click();await expect(page.getByRole('status')).toContainText('Saved');
 const apiIdea=await page.request.get('/api/v1/ideas'+new URL(page.url()).pathname.replace('/ideas',''));const latest=await apiIdea.json();
 await page.request.post('/api/v1/ideas/'+latest.id+'/comments',{headers:{'X-CSRF-Token':(await (await page.request.get('/api/v1/session/me')).json()).csrf},data:{record_version:latest.record_version,body:'Parallel edit for stale-form verification'}});
 await page.getByLabel('Screening note',{exact:true}).fill('Unsaved note retained after conflict');await page.getByRole('button',{name:'Save business case'}).click();await expect(page.getByRole('alert')).toContainText('Refresh');await expect(page.getByLabel('Screening note',{exact:true})).toHaveValue('Unsaved note retained after conflict');await page.reload();
 await page.getByRole('button',{name:'Move to Screening →',exact:true}).click();await page.getByLabel('Decision reason').fill('Ready for site screening');await page.getByRole('button',{name:'Confirm screening'}).click();await expect(page.locator('.idea-meta')).toContainText('Screening');
 await page.getByLabel('Add a comment').fill('Pilot owner is available this week.');await page.getByRole('button',{name:'Post comment'}).click();await expect(page.getByText('Pilot owner is available this week.',{exact:true})).toBeVisible();
 await page.getByRole('tab',{name:'Implementation',exact:true}).click();await page.getByLabel('Task title',{exact:true}).fill('Document baseline');await page.getByRole('button',{name:'Save task',exact:true}).click();await expect(page.getByRole('cell',{name:'Document baseline',exact:true})).toBeVisible();
 await page.reload();await expect(page.getByRole('cell',{name:'Document baseline',exact:true})).toBeVisible();await page.getByRole('tab',{name:'History',exact:true}).click();await expect(page.getByText('Task Changed',{exact:true})).toBeVisible();expect(errors).toEqual([]);
 const list=await (await page.request.get('/api/v1/ideas?page_size=100&search=Reduce%20changeover%20scrap')).json();
 const validation=list.items.find((i:any)=>i.stage==='Validation');await page.goto('/ideas/'+validation.id+'?tab=financials');
 let detail=await (await page.request.get('/api/v1/ideas/'+validation.id)).json();let pending=detail.results.find((r:any)=>!r.verified_at&&r.gross!==null);
 if(!pending){
   // Repeated runs preserve prior sign-offs and add a fresh elapsed period.
   let month='';for(let n=1;n<=120;n++){const d=new Date();d.setUTCDate(1);d.setUTCMonth(d.getUTCMonth()-n);const candidate=d.toISOString().slice(0,7)+'-01';if(!detail.results.some((r:any)=>r.month===candidate)){month=candidate;break;}}
   expect(month).toBeTruthy();const csrf=(await (await page.request.get('/api/v1/session/me')).json()).csrf;
   const saved=await page.request.put('/api/v1/ideas/'+validation.id+'/results/'+month,{headers:{'X-CSRF-Token':csrf},data:{record_version:detail.record_version,period_version:0,gross:'900.00',recurring:'100.00',spend:'0.00',reason:'Isolated browser verification fixture'}});expect(saved.ok()).toBeTruthy();
   detail=await (await page.request.get('/api/v1/ideas/'+validation.id)).json();pending=detail.results.find((r:any)=>r.month===month);await page.reload();
 }
 await page.getByLabel('Outcome month').fill(pending.month.slice(0,7));await page.getByRole('button',{name:'Review result verification'}).click();await page.getByLabel('Verification reason').fill('Browser review of measured pilot baseline');await page.getByRole('button',{name:'Confirm result verification'}).click();await expect(page.getByRole('status')).toContainText('Saved');
 const confirmed=await (await page.request.get('/api/v1/ideas/'+validation.id)).json();expect(confirmed.results.find((r:any)=>r.month===pending.month).verified_at).toBeTruthy();expect(errors).toEqual([]);
});
