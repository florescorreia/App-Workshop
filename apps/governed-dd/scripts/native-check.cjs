// Real tenant-native authentication/permission smoke; credentials never printed.
const fs=require('fs');
(async()=>{const origin=process.env.PAPERCLIP_PUBLIC_URL||process.env.PAPERCLIP_AUTH_PUBLIC_BASE_URL;
for(const name of process.argv.slice(2)){
 const u=JSON.parse(fs.readFileSync('/paperclip/native-'+name+'.json'));let cookie='';
 const login=await fetch('http://localhost:3100/api/auth/sign-in/email',{method:'POST',headers:{Origin:origin,'Content-Type':'application/json'},body:JSON.stringify({email:u.email,password:u.password})});
 if(!login.ok)throw Error('Native login failed '+name);cookie=login.headers.getSetCookie().map(c=>c.split(';')[0]).join('; ');
 const companies=await fetch('http://localhost:3100/api/companies',{headers:{Origin:origin,Cookie:cookie}});if(!companies.ok||(await companies.json()).length!==1)throw Error('Native membership failed '+name);
 console.log('Native login and single-company membership passed for '+name);
}})().catch(e=>{console.error(e.message);process.exitCode=1});
