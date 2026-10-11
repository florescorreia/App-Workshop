// Explicit tenant administrator provisioning through upstream bootstrap CLI and Better Auth API.
// Run only on a private backend while sign-up is temporarily enabled, before ingress attachment.
const fs=require('fs');const cp=require('child_process');const crypto=require('crypto');
(async()=>{
 const config={ $meta:{version:1,updatedAt:new Date().toISOString(),source:'configure'},
 database:{mode:'postgres',connectionString:process.env.DATABASE_URL},logging:{mode:'file',logDir:'/paperclip/logs'},
 server:{deploymentMode:'authenticated',exposure:'private',host:'0.0.0.0',port:3100,serveUi:true},
 auth:{baseUrlMode:'auto',disableSignUp:false}};
 const path='/paperclip/governed-bootstrap.json';fs.writeFileSync(path,JSON.stringify(config),{mode:0o600});
 const out=cp.execFileSync('node',['--import','./cli/node_modules/tsx/dist/loader.mjs','cli/src/index.ts','auth','bootstrap-ceo','--config',path],{cwd:'/app',encoding:'utf8',timeout:120000});
 const token=out.match(/pcp_bootstrap_[a-f0-9]+/)?.[0];
 if(!token){if(out.includes('already has an admin')){console.log('Native administrator already provisioned; no changes.');return;}console.error('Bootstrap CLI output (redacted):',out.replace(/pcp_bootstrap_[a-z0-9]+/g,'[redacted]').replace(/postgres(?:ql)?:\/\/[^\s]+/g,'[redacted]'));throw Error('Bootstrap did not produce invite');}
 const privatePath='/paperclip/native-admin-pending.json';
 const pending=fs.existsSync(privatePath)?JSON.parse(fs.readFileSync(privatePath)): {email:'bootstrap-'+crypto.randomBytes(6).toString('hex')+'@example.invalid',password:crypto.randomBytes(36).toString('base64url')};
 fs.writeFileSync(privatePath,JSON.stringify(pending),{mode:0o600});
 const secret=pending.password;
 const origin=process.env.PAPERCLIP_AUTH_PUBLIC_BASE_URL;
 const request=async(path,body,cookie='')=>{
  const r=await fetch('http://localhost:3100'+path,{method:'POST',headers:{'Content-Type':'application/json',Origin:origin,Referer:'http://localhost:3100/',Host:new URL(origin).host,...(cookie?{Cookie:cookie}:{})},body:JSON.stringify(body)});
  if(!r.ok){const error=await r.json().catch(()=>({}));throw Error('Native provisioning API failed: '+r.status+' '+path+' '+(error.message||error.error||error.code||''));}
  return {body:await r.json(),cookie:r.headers.getSetCookie().map(c=>c.split(';')[0]).join('; ')};
 };
 let user;
 try{user=await request('/api/auth/sign-in/email',{email:pending.email,password:secret})}catch{user=await request('/api/auth/sign-up/email',{name:'Engagement administrator',email:pending.email,password:secret})}
 await request('/api/invites/'+token+'/accept',{requestType:'human'},user.cookie);
 fs.writeFileSync('/paperclip/native-admin.json',JSON.stringify({email:pending.email,password:secret,userId:user.body.user.id}),{mode:0o600});
 console.log('Native administrator provisioned through upstream APIs. Credential stored privately; disable sign-up before exposing ingress.');
})().catch(e=>{console.error('Native bootstrap failed:',e.message.replace(/pcp_bootstrap_[a-z0-9]+/g,'[redacted]').replace(/postgres(?:ql)?:\/\/[^\s]+/g,'[redacted]'));process.exitCode=1});
