const {chromium}=require('playwright');const fs=require('fs'),http=require('http');
(async()=>{
 const tenant=process.env.DD_CHECK_TENANT;
 if(!/^[a-f0-9]{24}$/.test(tenant||''))throw Error('Explicit tenant required');
 const proxy=http.createServer((req,res)=>{const up=http.request({host:'gateway',port:8080,path:req.url,method:req.method,headers:req.headers},r=>{res.writeHead(r.statusCode,r.headers);r.pipe(res)});up.on('error',()=>{res.writeHead(502);res.end()});req.pipe(up)});
 await new Promise(r=>proxy.listen(8081,'127.0.0.1',r));const browser=await chromium.launch();
 try{
  const page=await browser.newPage();await page.goto('http://localhost:8081/auth/login');
  await page.locator('#username').fill('alice');await page.locator('#password').fill(fs.readFileSync('/private/alice.password','utf8').trim());await page.locator('#kc-login').click();
  await page.getByRole('heading',{name:'Engagements',exact:true}).waitFor();await page.goto('http://localhost:8081/t/'+tenant+'/');
  const sources=await page.evaluate(async tenant=>(await fetch('/t/'+tenant+'/api/records?kind=Source')).json(),tenant);
  if(!sources.length)throw Error('Existing user-uploaded source required');
  const before=sources.map(s=>[s.id,s.version,s.body.hash]);const source=sources[0];
  const sourceLink='http://localhost:8081/t/'+tenant+'/?object='+source.id+'&version='+source.version;
  await page.goto(sourceLink);await page.getByRole('dialog').waitFor();
  await page.context().grantPermissions(['clipboard-read','clipboard-write'],{origin:'http://localhost:8081'});
  if(await page.getByRole('textbox',{name:'Exact version link',exact:true}).inputValue()!==sourceLink)throw Error('Visible exact link incorrect');
  await page.getByRole('button',{name:'Copy link',exact:true}).click();
  await page.getByRole('status').filter({hasText:'Link copied.'}).waitFor();
  if(await page.evaluate(()=>navigator.clipboard.readText())!==sourceLink)throw Error('Clipboard exact link incorrect');
  await page.evaluate(()=>{navigator.clipboard.writeText=async()=>{throw Error('Clipboard denied')}});
  await page.getByRole('button',{name:'Copy link',exact:true}).click();
  await page.getByRole('status').filter({hasText:'Select the link above'}).waitFor();
  await page.setViewportSize({width:390,height:844});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Exact link mobile overflow');
  await page.setViewportSize({width:1440,height:1000});
  await page.getByRole('button',{name:'Close details'}).click();
  if(new URL(page.url()).searchParams.has('object'))throw Error('Close retained source URL');
  for(const section of ['Sources','Findings','Knowledge Graph','Definitions','Analyses','Deliverables','Overview']){
   await page.getByRole('navigation',{name:'Workspace'}).getByRole('button',{name:section,exact:true}).click();
   await page.getByRole('heading',{name:section,exact:true}).waitFor();
   if(await page.getByRole('dialog').count())throw Error('Source reopened on '+section);
  }
  await page.goto(sourceLink);await page.getByRole('dialog').waitFor();
  await page.getByRole('navigation',{name:'Workspace'}).getByRole('button',{name:'Sources',exact:true}).click();
  await page.getByRole('dialog').waitFor({state:'hidden'});
  if(new URL(page.url()).searchParams.has('object'))throw Error('Navigation retained source URL');
  let requested;const pending=new Promise(r=>requested=r);let release;
  const held=new Promise(r=>release=r);
  const route='**/api/records/'+source.id+'/'+source.version;
  await page.route(route,async r=>{requested();await held;await r.continue()});
  await page.getByRole('button',{name:source.body.filename,exact:true}).click();await pending;
  await page.getByRole('navigation',{name:'Workspace'}).getByRole('button',{name:'Findings',exact:true}).click();release();
  await page.waitForResponse(r=>r.url().endsWith('/api/records/'+source.id+'/'+source.version));
  await page.waitForTimeout(300);
  if(await page.getByRole('dialog').count()||new URL(page.url()).searchParams.has('object'))throw Error('Late source response reopened drawer');
  await page.unroute(route);
  const after=await page.evaluate(async tenant=>(await fetch('/t/'+tenant+'/api/records?kind=Source')).json(),tenant);
  if(JSON.stringify(before)!==JSON.stringify(after.map(s=>[s.id,s.version,s.body.hash])))throw Error('Sources changed');
  console.log('Visible exact link, clipboard copy/fallback, mobile layout, direct source links, Close, sidebar sections, delayed-response navigation and unchanged source hashes passed.');
 }finally{await browser.close();proxy.closeAllConnections();await new Promise(r=>proxy.close(r));}
})().then(()=>process.exit(0)).catch(e=>{console.error(e.message);process.exit(1)});
