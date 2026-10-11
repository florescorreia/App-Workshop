// Read authoritative native run metadata; emit only bounded provenance fields.
const fs=require('fs');
(async()=>{
 const id=process.argv[2];if(!/^[a-f0-9-]{36}$/.test(id))throw Error('Native run UUID required');
 const u=JSON.parse(fs.readFileSync('/paperclip/native-admin.json'));
 const login=await fetch('http://localhost:3100/api/auth/sign-in/email',{method:'POST',headers:{'Content-Type':'application/json',Origin:process.env.PAPERCLIP_PUBLIC_URL},body:JSON.stringify({email:u.email,password:u.password})});
 if(!login.ok)throw Error('Native authentication failed');
 const cookie=login.headers.getSetCookie().map(x=>x.split(';')[0]).join('; ');
 const response=await fetch('http://localhost:3100/api/heartbeat-runs/'+id,{headers:{Cookie:cookie}});
 if(!response.ok)throw Error('Native run unavailable');const run=await response.json();
 if(run.status!=='succeeded')throw Error('Native run did not succeed');
 const task=run.contextSnapshot?.issueId||run.contextSnapshot?.taskId;
 if(!task)throw Error('Native task linkage unavailable');
 console.log(JSON.stringify({paperclip_instance:process.env.PAPERCLIP_INSTANCE_ID,paperclip_run_id:id,task_id:task,agent_id:run.agentId,company_id:run.companyId,status:run.status,started_at:run.startedAt,finished_at:run.finishedAt}));
})().catch(e=>{console.error(e.message);process.exitCode=1});
