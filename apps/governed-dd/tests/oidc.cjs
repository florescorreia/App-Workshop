const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const http=require('http');
 const proxy=http.createServer((req,res)=>{const upstream=http.request({host:'gateway',port:8080,path:req.url,method:req.method,headers:req.headers},r=>{res.writeHead(r.statusCode,r.headers);r.pipe(res)});upstream.on('error',()=>{res.writeHead(502);res.end()});req.pipe(upstream)});
 await new Promise(resolve=>proxy.listen(8081,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1000}});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 page.on('console',message=>{if(message.type()==='error')console.log('Browser console:',message.text().replace(/Bearer\s+\S+/g,'Bearer [redacted]').slice(0,600))});
 page.on('response',r=>{if(r.status()>=400)console.log('Failed URL:',new URL(r.url()).host,new URL(r.url()).pathname,r.status())});
 await page.goto('http://localhost:8081/');
 await page.getByRole('link',{name:/Sign in to your workspace/}).click();
 try {await page.locator('#username').waitFor({timeout:15000})}catch(e){console.log('Login page:',page.url(),(await page.locator('body').innerText()).slice(0,1000));await page.screenshot({path:'/evidence/oidc-debug.png'});throw e}
 await page.locator('#username').fill('alice');await page.locator('#password').fill(fs.readFileSync('/private/alice.password','utf8'));
 await page.locator('#kc-login').click();
 if(await page.locator('#email').isVisible().catch(()=>false)){
  await page.locator('#email').fill('alice@example.invalid');await page.getByRole('button',{name:/Submit/}).click();
 }
 try {await page.getByRole('heading',{name:'Engagements',exact:true}).waitFor({timeout:15000})}catch(e){console.log('Callback page:',page.url(),(await page.locator('body').innerText()).slice(0,1000));await page.screenshot({path:'/evidence/oidc-debug.png'});throw e}
 const me=await page.evaluate(()=>fetch('/api/me').then(r=>r.json()));
 if(me.engagements.length!==1||me.engagements[0].id!=='a4e176281f3c47d081b3b623')throw Error('Alice membership list incorrect');
 for(const path of ['','api/records','api/search?q=revenue','paperclip/api/companies','lab/','api/bytes/00000000-0000-0000-0000-000000000000/1','mcp/']){
  const status=await page.evaluate(async path=>(await fetch('/t/b5e287392a4d58e192c4c734/'+path)).status,path);
  if(status!==404)throw Error('Unauthorized tenant route not hidden: '+path+' '+status);
 }
 await page.screenshot({path:'/evidence/alice-portal.png',fullPage:true});
 await page.getByRole('link',{name:/Fictional A/}).click();
 await page.getByRole('heading',{name:'Overview',exact:true}).waitFor();
 await page.getByRole('button',{name:'Findings',exact:true}).click();
 await page.getByRole('button',{name:'Fictional revenue increased 20%',exact:true}).click();
 await page.getByRole('dialog').waitFor();
 await page.getByRole('button',{name:'Expand connected evidence',exact:true}).click();
 await page.getByRole('img',{name:'Bounded evidence graph'}).waitFor();
 await page.screenshot({path:'/evidence/graph-desktop.png',fullPage:true});
 await page.screenshot({path:'/evidence/finding-desktop.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:'/evidence/finding-mobile.png',fullPage:true});
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
 if(errors.length)throw Error(errors.join('\n'));
 await page.getByRole('button',{name:'Close details'}).click();
 await page.setViewportSize({width:1440,height:1000});
 await page.getByRole('button',{name:'Overview',exact:true}).click();
 await page.getByRole('link',{name:'Open Paperclip',exact:true}).click();
 await page.goto('http://paperclip-a4e176281f3c47d081b3b623.localhost:8081/auth');
 await page.waitForTimeout(1500);
 const native=JSON.parse(fs.readFileSync('/native/native-alice.json','utf8'));
 const email=page.locator('input[type=email]');
 await email.waitFor({state:'visible',timeout:30000});
 {
  await email.fill(native.email);await page.locator('input[type=password]').fill(native.password);
  await page.getByRole('button',{name:/Sign in|Log in/i}).click();
 }
 await email.waitFor({state:'hidden',timeout:30000});await page.waitForTimeout(3000);
 await page.screenshot({path:'/evidence/native-paperclip-desktop.png',fullPage:true});
 if(await page.locator('input[type=email]').isVisible().catch(()=>false))throw Error('Native consultant login did not complete');
 if((await page.locator('body').innerText()).trim().length<20)throw Error('Native Paperclip rendered an empty page');
 if(errors.length)throw Error(errors.join('\n'));
 console.log('Real OIDC login, Alice portal filtering, guessed routes and finding desktop/mobile passed.');
 await browser.close();
 proxy.close();
})();
