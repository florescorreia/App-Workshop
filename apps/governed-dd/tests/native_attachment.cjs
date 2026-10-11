// Additive explicit fictional attachment fixture; reuse the exact existing bytes.
const fs=require('fs'),crypto=require('crypto');
(async()=>{
 const task='8656c192-e27a-4b3a-927a-924129fb9225';
 const u=JSON.parse(fs.readFileSync('/paperclip/native-admin.json'));
 const login=await fetch('http://localhost:3100/api/auth/sign-in/email',{method:'POST',headers:{'Content-Type':'application/json',Origin:process.env.PAPERCLIP_PUBLIC_URL},body:JSON.stringify({email:u.email,password:u.password})});if(!login.ok)throw Error('Native login failed');
 const headers={Origin:process.env.PAPERCLIP_PUBLIC_URL,Cookie:login.headers.getSetCookie().map(x=>x.split(';')[0]).join('; ')};
 const issue=await fetch('http://localhost:3100/api/issues/'+task,{headers});if(!issue.ok)throw Error('Fixture task missing');const row=await issue.json();
 const data=Buffer.from('FICTIONAL attachment acceptance fixture v1\nRevenue prior 100, current 120 USD million.\n'),hash=crypto.createHash('sha256').update(data).digest('hex');
 const list=await fetch('http://localhost:3100/api/issues/'+task+'/attachments',{headers});if(!list.ok)throw Error('Attachments missing');let attachment=(await list.json()).find(x=>x.sha256===hash&&x.originalFilename==='fictional-attachment-v1.txt');
 if(!attachment){const form=new FormData();form.set('file',new Blob([data],{type:'text/plain'}),'fictional-attachment-v1.txt');const r=await fetch('http://localhost:3100/api/companies/'+row.companyId+'/issues/'+task+'/attachments',{method:'POST',headers,body:form});if(!r.ok)throw Error('Native attachment upload failed '+r.status);attachment=await r.json()}
 fs.writeFileSync('/paperclip/fixture-attachment-v1.json',JSON.stringify({task,attachment:attachment.id}));
 console.log(JSON.stringify({task,attachment:attachment.id}));
})().catch(e=>{console.error(e.message);process.exitCode=1});
