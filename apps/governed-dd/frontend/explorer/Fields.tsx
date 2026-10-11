import React from 'react';
export function FieldValue({value,open}:{value:any,open:(r:any)=>void}):React.ReactNode{
 if(value===null||value===undefined)return <span className="muted">Not recorded</span>;
 if(typeof value!=='object')return <p className="detail-text">{String(value)}</p>;
 if(value.id&&value.version)return <button className="text-link" onClick={()=>open(value)}>Open exact version {value.version}{value.locator?' · '+value.locator:''} →</button>;
 if(Array.isArray(value))return value.length?<ul className="detail-list">{value.map((v,i)=><li key={i}><FieldValue value={v} open={open}/></li>)}</ul>:<span className="muted">None recorded</span>;
 return <dl className="detail-properties">{Object.entries(value).map(([k,v])=><React.Fragment key={k}><dt>{k.replaceAll('_',' ')}</dt><dd><FieldValue value={v} open={open}/></dd></React.Fragment>)}</dl>
}
