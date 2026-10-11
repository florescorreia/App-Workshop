// Explicit transient native identity provisioning while ingress is detached and sign-up enabled.
const fs=require('fs');const crypto=require('crypto');
(async()=>{
 const [name,role='viewer']=process.argv.slice(2);if(!/^[a-z][a-z0-9-]{1,40}$/.test(name)||!['owner','analyst','reviewer','viewer'].includes(role))throw Error('Invalid native user/role');
 const admin=JSON.parse(fs.readFileSync('/paperclip/native-admin.json'));const origin=process.env.PAPERCLIP_PUBLIC_URL||process.env.PAPERCLIP_AUTH_PUBLIC_BASE_URL;
 let cookie='';async function api(path,body,method=body?'POST':'GET'){
  const r=await fetch('http://localhost:3100/api'+path,{method,headers:{'Content-Type':'application/json',Origin:origin,Referer:'http://localhost:3100/',Cookie:cookie},...(body?{body:JSON.stringify(body)}:{})});
  if(!r.ok){const b=await r.json().catch(()=>({}));throw Error(path+' '+r.status+' '+(b.error||b.message||''));}
  if(r.headers.getSetCookie().length)cookie=r.headers.getSetCookie().map(c=>c.split(';')[0]).join('; ');return r.json();
 }
 await api('/auth/sign-in/email',{email:admin.email,password:admin.password});const adminCookie=cookie;const company=(await api('/companies'))[0];if(!company)throw Error('Provision native company first');
 const path='/paperclip/native-'+name+'.json';let user=fs.existsSync(path)?JSON.parse(fs.readFileSync(path)): {name,email:name+'@example.invalid',password:crypto.randomBytes(36).toString('base64url')};
 fs.writeFileSync(path,JSON.stringify(user),{mode:0o600});
 const invite=await api('/companies/'+company.id+'/invites',{allowedJoinTypes:'human',humanRole:role==='owner'?'owner':role==='viewer'?'viewer':'operator'});
 cookie='';try{await api('/auth/sign-in/email',{email:user.email,password:user.password})}catch{await api('/auth/sign-up/email',{name,email:user.email,password:user.password})}
 const joined=await api('/invites/'+invite.token+'/accept',{requestType:'human'});
 cookie=adminCookie;
 if(joined.status==='pending_approval')await api('/companies/'+company.id+'/join-requests/'+joined.id+'/approve',{});
 console.log('Native tenant user provisioned through APIs; credential stays private. Disable sign-up before ingress.');
})().catch(e=>{console.error('Native user provisioning failed:',e.message.replace(/pcp_[a-z0-9_]+/g,'[redacted]'));process.exitCode=1});
