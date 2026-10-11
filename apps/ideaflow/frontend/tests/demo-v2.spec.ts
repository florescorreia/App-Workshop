import {test,expect} from '@playwright/test';
import fs from 'node:fs';

test('additive v2 appears in register, Pipeline, Process and Value without business writes',async({page})=>{
 test.skip(process.env.DEMO_V2_LIVE!=='true','Explicit v2 live check only');
 const env=Object.fromEntries(fs.readFileSync('/config/.env','utf8').split(/\r?\n/).filter(l=>l.includes('=')).map(l=>{const n=l.indexOf('=');return[l.slice(0,n),l.slice(n+1)];}));
 const report=JSON.parse(fs.readFileSync('/config/local/harborworks-v2-verification.json','utf8'));
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/');await page.getByLabel('Email',{exact:true}).fill(env.ADMIN_EMAIL);await page.getByLabel('Password',{exact:true}).fill(env.ADMIN_PASSWORD);await page.getByRole('button',{name:'Sign in →',exact:true}).click();await expect(page.getByRole('heading',{name:'A clearer path from idea to impact'})).toBeVisible();
 const cohort='ids='+report.records.map((r:any)=>r.id).join(',');
 for(const width of [1440,1280]){
   await page.setViewportSize({width,height:width===1440?900:720});
   for(const [path,name] of [['/ideas?'+cohort,'register'],['/pipeline?'+cohort,'pipeline'],['/process?'+cohort,'process'],['/value?'+cohort,'value']]){
     await page.goto(path);await expect(page.locator('h1')).toBeVisible();await expect(page.locator('.loading')).toHaveCount(0);
     if(name==='register'){await expect(page.getByText('12 ideas in this view')).toBeVisible();for(const r of report.records)await expect(page.getByRole('link').filter({hasText:r.title}).first()).toBeVisible();}
     if(name==='pipeline'){await expect(page.locator('.idea-card')).toHaveCount(12);await expect(page.locator('.pipeline-column').filter({has:page.getByRole('heading',{name:'New 6',exact:true})}).locator('.idea-card')).toHaveCount(6);}
     if(name==='process'){await expect(page.locator('.react-flow__node').first()).toBeVisible();await expect(page.locator('.as-of')).toContainText('12 selected cases');}
     if(name==='value'){await expect(page.locator('.as-of')).toContainText('2 of 2 eligible idea-months reported; 1 verified');const hero=report.records.find((r:any)=>r.stage==='Implementation');await expect(page.getByRole('link',{name:hero.reference+' · '+hero.title,exact:true})).toBeVisible();await expect(page.getByRole('cell',{name:'Unapproved',exact:true})).toHaveCount(11);await expect(page.getByRole('cell',{name:'$46,750.00',exact:true})).toBeVisible();}
     expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2)).toBe(false);await page.waitForTimeout(300);await page.screenshot({path:`/artifacts/v2-${name}-${width}.png`});
   }
 }
 const selected=report.records.find((r:any)=>r.stage==='New');await page.goto('/ideas/'+selected.id);await page.getByRole('button',{name:'Move to Screening →',exact:true}).click();await page.getByLabel('Decision reason').fill('Named sponsor and order baseline are ready for screening');await expect(page.getByRole('button',{name:'Confirm screening'})).toBeEnabled();await page.getByRole('button',{name:'Close dialog',exact:true}).click();
 await page.goto('/ideas/'+report.implementation.id+'?tab=financials');await page.getByLabel('Outcome month').fill('2026-09');await page.getByRole('button',{name:'Review result verification'}).click();await expect(page.getByLabel('Reviewed gross (USD)')).toHaveValue('7200.00');await page.getByLabel('Verification reason').fill('Preview only; leave September unverified for presentation');await expect(page.getByRole('button',{name:'Confirm result verification'})).toBeEnabled();await page.getByRole('button',{name:'Close dialog',exact:true}).click();expect(errors).toEqual([]);
});
