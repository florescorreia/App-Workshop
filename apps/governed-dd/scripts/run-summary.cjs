const fs=require('fs');const path=require('path');
const state=JSON.parse(fs.readFileSync(process.argv[2]==='review'?'/paperclip/governed-review-check.json':'/paperclip/governed-run-check.json'));
const log=path.join('/paperclip/instances',process.env.PAPERCLIP_INSTANCE_ID,'data/run-logs',state.company,state.agent,state.run+'.ndjson');
if(!fs.existsSync(log)){console.log('Run log not available yet; inspect native task status.');process.exit(0)}
const entries=fs.readFileSync(log,'utf8').split('\n').filter(Boolean).map(l=>JSON.parse(l));
for(const entry of entries){
 try{const event=JSON.parse(entry.chunk);if(event.item?.type==='agent_message')console.log(event.item.text.replace(/Bearer\s+\S+/g,'Bearer [redacted]'));else if(event.type==='turn.completed')console.log('Turn completed');else if(event.item?.type==='mcp_tool_call'){console.log('Tool:',event.item.tool,'status:',event.item.status,'error:',event.item.error?JSON.stringify(event.item.error):'none');if(event.item.tool==='register_analysis'&&event.item.status==='failed')console.log(JSON.stringify({arguments:event.item.arguments,result:event.item.result}).replace(/Bearer\s+\S+/g,'Bearer [redacted]').slice(0,6000));}}
 catch{if(entry.chunk.startsWith('[paperclip]'))console.log(entry.chunk.slice(0,180));}
}
