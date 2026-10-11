// Explicit administrator import; supported native APIs, never logs credentials/bytes.
const fs=require('fs'),crypto=require('crypto');
(async()=>{
 const [task,id,directory]=process.argv.slice(2);
 if(![task,id].every(x=>/^[a-f0-9-]{36}$/.test(x))||!directory.startsWith('/tmp/dd-import-'))throw Error('Exact native task/attachment required');
 const u=JSON.parse(fs.readFileSync('/paperclip/native-admin.json'));
 const login=await fetch('http://localhost:3100/api/auth/sign-in/email',{method:'POST',headers:{'Content-Type':'application/json',Origin:process.env.PAPERCLIP_PUBLIC_URL},body:JSON.stringify({email:u.email,password:u.password})});
 if(!login.ok)throw Error('Native authentication failed');
 const cookie=login.headers.getSetCookie().map(x=>x.split(';')[0]).join('; ');
 const list=await fetch('http://localhost:3100/api/issues/'+task+'/attachments',{headers:{Cookie:cookie}});
 if(!list.ok)throw Error('Task unavailable');
 const attachment=(await list.json()).find(x=>x.id===id&&x.issueId===task);
 if(!attachment||attachment.byteSize<1||attachment.byteSize>20*1024*1024)throw Error('Attachment unavailable or oversized');
 const response=await fetch('http://localhost:3100/api/attachments/'+id+'/content',{headers:{Cookie:cookie}});
 if(!response.ok)throw Error('Attachment bytes unavailable');
 const parts=[];let size=0;
 for await(const part of response.body){size+=part.length;if(size>20*1024*1024)throw Error('Attachment download exceeds limit');parts.push(part)}
 const bytes=Buffer.concat(parts),hash=crypto.createHash('sha256').update(bytes).digest('hex');
 if(size!==attachment.byteSize||hash!==attachment.sha256)throw Error('Native attachment checksum/size mismatch');
 fs.mkdirSync(directory,{mode:0o700});fs.writeFileSync(directory+'/bytes',bytes,{mode:0o600});
 fs.writeFileSync(directory+'/metadata.json',JSON.stringify({filename:attachment.originalFilename||'attachment.txt',media_type:attachment.contentType,hash,size,paperclip_instance:process.env.PAPERCLIP_INSTANCE_ID,task_id:task,attachment_id:id,access_limitations:'Engagement team only; imported native attachment'}),{mode:0o600});
 console.log('Native attachment task binding, size and checksum verified.');
})().catch(e=>{console.error(e.message);process.exitCode=1});
