export type RecordData = Record<string, any>;
let csrf='';
export let appTimezone='America/New_York';
export function setSession(data:RecordData){csrf=data.csrf;appTimezone=data.timezone||appTimezone;}
export async function api(path:string, options:RequestInit={}):Promise<any>{
  const response=await fetch('/api/v1'+path,{...options,headers:{'Content-Type':'application/json','X-CSRF-Token':csrf,...options.headers}});
  if(!response.ok){
    const data=await response.json().catch(()=>({detail:response.statusText}));
    const detail=Array.isArray(data.detail)?data.detail.map((x:any)=>`${x.loc.slice(1).join('.')}: ${x.msg}`).join('; '):data.detail;
    throw new Error(detail||'The request could not be completed. Try again.');
  }
  return response.json();
}
export function send(path:string,data:any,method='POST'){return api(path,{method,body:JSON.stringify(data)});}
export function money(value:any,compact=false){
  if(value===null||value===undefined||value==='')return 'Unknown';
  return new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',notation:compact?'compact':'standard',maximumFractionDigits:compact?1:2}).format(Number(value));
}
export function dateText(value:any,time=false){
  if(!value)return 'Not set';
  if(value.length===10)return new Date(value+'T12:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
  return new Date(value).toLocaleString('en-US',{timeZone:appTimezone,month:'short',day:'numeric',year:'numeric',...(time?{hour:'numeric',minute:'2-digit'}:{})});
}
export function paybackText(value:any){return value?new Date(value+'T12:00:00').toLocaleDateString('en-US',{month:'long',year:'numeric'})+' month-end':'Unknown';}
export function numberOrNull(value:any){return value===''||value==null?null:String(value);}
