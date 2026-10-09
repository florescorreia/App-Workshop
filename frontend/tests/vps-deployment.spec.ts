import {test,expect} from '@playwright/test';

test('copied VPS workspace renders over trusted HTTPS and signs out',async({page})=>{
 test.setTimeout(180000);
 const failures:string[]=[];
 const policyViolations:string[]=[];
 await page.exposeFunction('recordPolicyViolation',(directive:string)=>policyViolations.push(directive));
 await page.addInitScript(()=>document.addEventListener('securitypolicyviolation',event=>{
   (window as any).recordPolicyViolation(event.violatedDirective);
 }));
 page.on('pageerror',e=>failures.push(e.message));
 page.on('response',r=>{if(r.url().includes('/api/v1/')&&r.status()>=500)failures.push(`${r.status()} ${r.url()}`);});
 await page.goto('/');
 const publicResponse=await page.request.get('/');
 expect(publicResponse.headers()['content-security-policy']).toContain("script-src 'self'");
 expect(publicResponse.headers()['strict-transport-security']).toBe('max-age=86400');
 expect(publicResponse.headers()['server']).toBeUndefined();
 expect(publicResponse.headers()['via']).toBeUndefined();
 for(const path of ['/api/docs','/api/openapi.json','/.env','/.git/config']){
   expect((await page.request.get(path)).status()).toBe(404);
 }
 await page.getByLabel('Email',{exact:true}).fill(process.env.IDEAFLOW_VPS_ADMIN_EMAIL!);
 await page.getByLabel('Password',{exact:true}).fill(process.env.IDEAFLOW_VPS_ADMIN_PASSWORD!);
 await page.getByRole('button',{name:'Sign in →',exact:true}).click();
 await expect(page.locator('h1')).toHaveText('A clearer path from idea to impact');
 const cookies=await page.context().cookies();
 const session=cookies.find(c=>c.name==='__Host-ideaflow_session');
 expect(session).toBeTruthy();expect(session!.secure).toBe(true);expect(session!.httpOnly).toBe(true);expect(session!.sameSite).toBe('Strict');
 const listResponse=await page.request.get('/api/v1/ideas?page_size=100');expect(listResponse.ok()).toBeTruthy();
 const list=await listResponse.json();expect(list.total).toBe(2);
 expect(list.items.map((i:any)=>i.reference).sort()).toEqual(['IF-00205','IF-00206']);
 const businessBefore:any={};
 for(const idea of list.items){businessBefore[idea.id]=await(await page.request.get('/api/v1/ideas/'+idea.id)).json();}
 for(const path of ['/dashboards/portfolio','/dashboards/process','/dashboards/value','/my-work','/references']){
   const response=await page.request.get('/api/v1'+path);expect(response.ok(),path).toBeTruthy();
 }
 const observedProcess=await(await page.request.get('/api/v1/dashboards/process')).json();expect(observedProcess.case_count).toBe(2);expect(observedProcess.rework.numerator).toBe(1);
 const idea=list.items.find((i:any)=>i.reference==='IF-00205');
 const paths=['/','/ideas','/pipeline','/process','/value','/guide','/settings','/ideas/'+idea.id+'?tab=financials','/ideas/'+idea.id+'?tab=history'];
 for(const width of [1440,1280,390]){
   await page.setViewportSize({width,height:width===1440?900:width===1280?720:844});
   for(const [index,path] of paths.entries()){
     await page.goto(path);await expect(page.locator('h1').first()).toBeVisible();await expect(page.locator('.loading')).toHaveCount(0);
     await expect(page.getByRole('alert')).toHaveCount(0);
     await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),{message:`Page width: ${path} ${width}`}).toBe(true);
     await page.screenshot({path:`/artifacts/vps-${width}-${index}.png`});
   }
 }
 for(const idea of list.items){const after=await(await page.request.get('/api/v1/ideas/'+idea.id)).json();const {financials:ignoredBefore,...before}=businessBefore[idea.id];const {financials:ignoredAfter,...savedAfter}=after;expect(savedAfter).toEqual(before);}
 await page.setViewportSize({width:1440,height:900});await page.goto('/');await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('button',{name:'Sign in →',exact:true})).toBeVisible();
 expect((await page.request.get('/api/v1/session/me')).status()).toBe(401);
 expect(failures).toEqual([]);
 expect(policyViolations).toEqual([]);
 console.log('VPS HTTPS, copied references, dashboards, desktop/mobile views and logout passed; no business mutations.');
});
