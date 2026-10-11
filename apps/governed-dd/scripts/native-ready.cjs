(async()=>{for(let i=0;i<60;i++){try{const r=await fetch('http://localhost:3100/api/health');if(r.ok)return}catch{}await new Promise(r=>setTimeout(r,1000))}process.exitCode=1})()
