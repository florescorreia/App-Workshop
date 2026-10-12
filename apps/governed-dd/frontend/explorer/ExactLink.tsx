import React,{useState} from 'react';

export function ExactLink({tenant,id,version}:{tenant:string,id:string,version:number}){
 const [status,setStatus]=useState('');
 const link=location.origin+'/t/'+tenant+'/?object='+encodeURIComponent(id)+'&version='+version;
 return <div className="exact-link">
  <label>Exact version link<input aria-label="Exact version link" readOnly value={link} onFocus={e=>e.currentTarget.select()}/></label>
  <button onClick={async()=>{try{await navigator.clipboard.writeText(link);setStatus('Link copied.')}catch{setStatus('Select the link above and copy it with Ctrl+C or your device’s copy command.')}}}>Copy link</button>
  <span role="status">{status}</span>
  <p>Paste this link into your Paperclip task to reference this exact version. Access requires engagement membership.</p>
 </div>;
}
