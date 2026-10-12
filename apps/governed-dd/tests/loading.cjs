const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch();const page=await browser.newPage();
 await page.goto('http://gateway:8080/',{waitUntil:'networkidle'});
 await page.getByRole('link',{name:/Sign in to your workspace/}).waitFor();
 await page.route('**/api/me',async route=>{await new Promise(r=>setTimeout(r,12000));try{await route.fulfill({status:401,body:'{}'})}catch{}});
 await page.reload({waitUntil:'domcontentloaded'});
 await page.getByRole('button',{name:'Retry connection'}).waitFor({timeout:15000});
 await page.getByRole('alert').filter({hasText:'too long'}).waitFor();
 await page.unroute('**/api/me');await page.getByRole('button',{name:'Retry connection'}).click();
 await page.getByRole('link',{name:/Sign in to your workspace/}).waitFor();
 console.log('Normal landing, stalled session timeout and successful retry passed.');await browser.close();
})().catch(e=>{console.error(e.message);process.exit(1)});
