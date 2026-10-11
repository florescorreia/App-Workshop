// Supported native run status/cancel; no credentials, full config or logs emitted.
const fs=require('fs');
(async()=>{const command=process.argv[2]||'status';if(!['status','cancel'].includes(command))throw Error('status or cancel required');
 const state=JSON.parse(fs.readFileSync(process.argv[3]==='review'?'/paperclip/governed-review-check.json':'/paperclip/governed-run-check.json'));
 const u=JSON.parse(fs.readFileSync('/paperclip/native-admin.json'));const origin=process.env.PAPERCLIP_PUBLIC_URL;let cookie='';
 async function api(path,body){const r=await fetch('http://localhost:3100/api'+path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json',Origin:origin,Cookie:cookie},...(body?{body:JSON.stringify(body)}:{})});if(!r.ok)throw Error('Native run API '+r.status);if(r.headers.getSetCookie().length)cookie=r.headers.getSetCookie().map(c=>c.split(';')[0]).join('; ');return r.json()}
 await api('/auth/sign-in/email',{email:u.email,password:u.password});
 const run=await api('/heartbeat-runs/'+state.run+(command==='cancel'?'/cancel':''),command==='cancel'?{}:undefined);
 console.log(JSON.stringify({status:run.status,errorCode:run.errorCode,startedAt:run.startedAt,finishedAt:run.finishedAt}));
})().catch(e=>{console.error(e.message);process.exitCode=1});
