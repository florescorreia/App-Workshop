// Read-only consultant handover check; creates no task or evidence.
const {chromium}=require('playwright');
const fs=require('fs'),http=require('http');
(async()=>{
 const tenant=process.env.DD_CHECK_TENANT;
 if(!/^[a-f0-9]{24}$/.test(tenant||''))throw Error('Explicit tenant required');
 const proxy=http.createServer((req,res)=>{
  const up=http.request({host:'gateway',port:8080,path:req.url,method:req.method,headers:req.headers},r=>{res.writeHead(r.statusCode,r.headers);r.pipe(res)});
  up.on('error',()=>{res.writeHead(502);res.end()});req.pipe(up);
 });
 await new Promise(r=>proxy.listen(8081,'127.0.0.1',r));
 const browser=await chromium.launch();
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}});
  await page.goto('http://localhost:8081/auth/login');
  await page.locator('#username').fill('alice');
  await page.locator('#password').fill(fs.readFileSync('/private/alice.password','utf8').trim());
  await page.locator('#kc-login').click();
  await page.getByRole('heading',{name:'Engagements',exact:true}).waitFor();
  const me=await page.evaluate(()=>fetch('/api/me').then(r=>r.json()));
  const engagement=me.engagements.find(t=>t.id===tenant);
  if(!engagement?.active||engagement.role!=='owner')throw Error('Active owner membership missing');
  await page.getByRole('link',{name:engagement.name,exact:false}).click();
  await page.getByRole('heading',{name:'Overview',exact:true}).waitFor();
  const records=await page.evaluate(async tenant=>{
   const r=await fetch('/t/'+tenant+'/api/records');if(!r.ok)throw Error('Registry unavailable');return r.json();
  },tenant);
  if(!Array.isArray(records)||records.length)throw Error('Engagement must contain zero records');
  await page.screenshot({path:'/evidence/harborlight-empty-desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
  await page.screenshot({path:'/evidence/harborlight-empty-mobile.png',fullPage:true});
  await page.setViewportSize({width:1440,height:1000});
  console.log('Explorer login and empty desktop/mobile workspace passed.');
  await page.getByRole('link',{name:'Open Paperclip',exact:true}).click();
  await page.goto('http://paperclip-'+tenant+'.localhost:8081/auth');
  const native=JSON.parse(fs.readFileSync('/native/native-alice.json','utf8'));
  await page.locator('input[type=email]').fill(native.email);
  await page.locator('input[type=password]').fill(native.password);
  await page.getByRole('button',{name:/Sign in|Log in/i}).click();
  await page.locator('input[type=email]').waitFor({state:'hidden',timeout:30000});
  console.log('Native sign-in form completed.');
  const companies=await page.evaluate(()=>fetch('/api/companies').then(r=>r.json()));
  if(!Array.isArray(companies)||companies.length!==1)throw Error('Native company unavailable');
  console.log('Native company access passed.');
  const data=await page.evaluate(async id=>{
   const agents=await fetch('/api/companies/'+id+'/agents').then(r=>r.json());
   const issues=await fetch('/api/companies/'+id+'/issues').then(r=>r.json());return {agents,issues};
  },companies[0].id);
  if(!Array.isArray(data.issues)||data.issues.length)throw Error('Native task list must be empty');
  for(const name of ['DD analyst','DD reviewer']){
   const a=data.agents.find(a=>a.name===name);
   if(!a||a.runtimeConfig?.heartbeat?.enabled!==false)throw Error('Agent missing or scheduled heartbeat enabled');
  }
  await page.screenshot({path:'/evidence/harborlight-paperclip-empty.png',fullPage:true});
  console.log('Alice portal/native login, active owner access, zero records/tasks, both unscheduled agents and desktop/mobile layout passed.');
 }finally{await browser.close();proxy.closeAllConnections();await new Promise(r=>proxy.close(r));}
})().then(()=>process.exit(0)).catch(e=>{console.error('Empty-engagement browser check failed:',e.message.replace(/Bearer\s+\S+/g,'Bearer [redacted]').slice(0,800));process.exit(1)});
