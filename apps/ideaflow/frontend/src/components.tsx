import {useEffect,useRef, useState,cloneElement,isValidElement,type ReactElement,type ReactNode} from 'react';
import {Link, useSearchParams} from 'react-router-dom';

import type * as PlotlyType from 'plotly.js';
const Plotly = (window as unknown as {Plotly:typeof PlotlyType}).Plotly;
import {money,dateText,RecordData} from './api';

export function Chip({children}:{children:ReactNode}){return <span className={'chip '+String(children).toLowerCase().replaceAll(' ','-')}>{children}</span>;}
export function Empty({title='A clear starting point',children}:{title?:string;children?:ReactNode}){return <div className="empty"><div className="empty-symbol">↗</div><h3>{title}</h3><p>{children||'Add your first idea to start building a measured improvement portfolio.'}</p><Link className="button primary" to="/ideas/new">Create an idea</Link></div>;}
export function ErrorBox({error}:{error:string}){return error?<div role="alert" className="error">{error}</div>:null;}
export function Field({label,children,hint}:{label:string;children:ReactNode;hint?:string}){return <label className="field"><span>{label}</span>{isValidElement(children)?cloneElement(children as ReactElement<any>,{'aria-label':label}):children}{hint&&<small>{hint}</small>}</label>;}
export function Modal({title,children,onClose}:{title:string;children:ReactNode;onClose:()=>void}){
 const ref=useRef<HTMLDialogElement>(null);
 useEffect(()=>{const el=ref.current;el?.showModal();return()=>el?.close();},[]);
 return <dialog ref={ref} onCancel={onClose} aria-label={title}><div className="modal-title"><h2>{title}</h2><button aria-label="Close dialog" onClick={onClose}>×</button></div>{children}</dialog>;
}
export function FilterBar({refs,extended=false,cohort=false}:{refs:RecordData;extended?:boolean;cohort?:boolean}){
 const [params,setParams]=useSearchParams();
 const fields=[['site_id','Location',refs.sites],['business_unit','Business unit',[...new Set(refs.sites.map((s:any)=>s.business_unit).filter(Boolean))].map(x=>({id:x,label:x}))],['category_id','Category',refs.categories],
 ...(extended?[['owner_id','Owner',refs.users.filter((u:any)=>!u.deleted_at).map((u:any)=>({...u,label:u.name}))],['stage','Stage',refs.stages.map((s:string)=>({id:s,label:s}))],['disposition','Disposition',['Active','On hold','Rejected','Cancelled'].map(s=>({id:s,label:s}))]]:[])];
 const change=(key:string,value:string)=>{const next=new URLSearchParams(params);value?next.set(key,value):next.delete(key);next.delete('page');setParams(next);};
 return <><div className="filters">{extended&&<Field label="Search"><input placeholder="Title, problem or reference" value={params.get('search')||''} onChange={e=>change('search',e.target.value)}/></Field>}
 {fields.map(([key,label,items])=><Field key={String(key)} label={String(label)}><select value={params.get(String(key))||''} onChange={e=>change(String(key),e.target.value)}><option value="">All {label==='Category'?'categories':String(label).toLowerCase()+'s'}</option>{(items as any[]).map((i:any)=><option key={i.id} value={i.id}>{i.label}</option>)}</select></Field>)}
 {cohort&&['created_from','created_to'].map((key,i)=><Field key={key} label={i?'Created through':'Created from'}><input type="date" value={params.get(key)||''} onChange={e=>change(key,e.target.value)}/></Field>)}
 {params.size>0&&<button onClick={()=>setParams({})}>Reset filters</button>}
 {params.get('ids')&&<p className="filter-note">Showing contributing ideas from analytics. Reset to see the full register.</p>}</div></>;
}
export function Metric({label,value,note}:{label:string;value:ReactNode;note?:string}){return <div className="metric"><span>{label}</span><strong>{value}</strong>{note&&<small>{note}</small>}</div>;}
export function IdeasTable({items,returnTo}:{items:RecordData[];returnTo?:string}){
 return <div className="table-scroll"><table><thead><tr>{['Idea / reference','Owner','Location','Stage / disposition','Annual net potential','Expected finish','Stage age'].map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{items.map(i=><tr key={i.id}><td><Link to={'/ideas/'+i.id} state={{returnTo}}><strong>{i.title}</strong><small>{i.reference}{i.demo_batch_id&&' · Fictional demo data'}</small></Link></td><td>{i.owner_name}</td><td>{i.site}</td><td><Chip>{i.stage}</Chip><small>{i.disposition}</small></td><td className="numeric">{money(i.annual_net_potential)}</td><td>{dateText(i.expected_finish)}</td><td>{Math.floor(i.stage_age_days)} days</td></tr>)}</tbody></table></div>;
}
export function Chart({data,title,onClick,height=270,categorical=false,xRange}:{data:any[];title:string;onClick?:(event:any)=>void;height?:number;categorical?:boolean;xRange?:[string,string]}){
 const ref=useRef<HTMLDivElement>(null);
 useEffect(()=>{
  const el=ref.current;if(!el)return;
  Plotly.react(el,data,{height,autosize:true,margin:{l:64,r:20,t:16,b:48},paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{family:'Inter, sans-serif',color:'#405469',size:11},
   xaxis:{automargin:true,...(categorical?{type:'category' as const}:{}),...(xRange?{type:'date' as const,range:xRange}: {})},yaxis:{automargin:true,gridcolor:'#e6ecec'},legend:{orientation:'h',y:1.15},barmode:'group'},{responsive:true,displayModeBar:false});
  if(onClick)(el as any).on('plotly_click',onClick);
  let mounted=true;
  const observer=new ResizeObserver(()=>{
   if(mounted&&el.isConnected&&el.getBoundingClientRect().width>0){
    Promise.resolve(Plotly.Plots.resize(el)).catch(()=>{/* Plot may unmount during Plotly's delayed resize. */});
   }
  });observer.observe(el);
  return()=>{mounted=false;observer.disconnect();Plotly.purge(el);};
 },[JSON.stringify(data),height,categorical,JSON.stringify(xRange)]);
 return <div role="img" aria-label={title} ref={ref} className="chart"/>;
}
export function Section({title,note,children}:{title:string;note?:string;children:ReactNode}){return <section className="panel"><div className="section-head"><h2>{title}</h2>{note&&<p>{note}</p>}</div>{children}</section>;}
