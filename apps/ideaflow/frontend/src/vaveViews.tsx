import {useEffect,useState} from 'react';
import {Link} from 'react-router-dom';
import {api,send,dateText,RecordData} from './api';
import {ErrorBox,Field,Section} from './components';

const money=(v:any,c='EUR')=>v==null?'Unknown':new Intl.NumberFormat('en-US',{style:'currency',currency:c}).format(Number(v));
const levels=['Captured','Screened','Quantified','Validated','Authorized','Implemented','Verified'];
export const categories=['Design simplification','Material substitution','Specification optimization','Part commonization','Manufacturing process','Sourcing','Make or buy','Logistics','Packaging','Scrap and yield','Software or electronics'];

export function PortfolioControls({query,change,members,external}:{query:URLSearchParams;change:(key:string,value:string)=>void;members:any[];external:boolean}){
 return <div className="filters vave-filters">
  <Field label="Search ideas"><input placeholder="Title, part, supplier or scope" value={query.get('search')||''} onChange={e=>change('search',e.target.value)}/></Field>
  <Field label="Maturity"><select value={query.get('maturity')||''} onChange={e=>change('maturity',e.target.value)}><option value="">All maturity levels</option>{levels.map((l,n)=><option key={l} value={n}>M{n} {l}</option>)}</select></Field>
  <Field label="Activity status"><select value={query.get('status')||''} onChange={e=>change('status',e.target.value)}><option value="">All statuses</option>{['Draft','Active','On hold','Rejected','Cancelled','Superseded','Closed'].map(v=><option key={v}>{v}</option>)}</select></Field>
  <Field label="Product"><input value={query.get('product')||''} onChange={e=>change('product',e.target.value)}/></Field>
  <Field label="Category"><select value={query.get('category')||''} onChange={e=>change('category',e.target.value)}><option value="">All categories</option>{categories.map(v=><option key={v}>{v}</option>)}</select></Field>
  {!external&&<><Field label="Plant"><input value={query.get('plant')||''} onChange={e=>change('plant',e.target.value)}/></Field><Field label="Part"><input value={query.get('part')||''} onChange={e=>change('part',e.target.value)}/></Field><Field label="Supplier"><input value={query.get('supplier')||''} onChange={e=>change('supplier',e.target.value)}/></Field><Field label="Owner"><select value={query.get('owner_id')||''} onChange={e=>change('owner_id',e.target.value)}><option value="">All owners</option>{members.map(m=><option key={m.id} value={m.id}>{m.name}</option>)}</select></Field></>}
  <Field label="Sort ideas"><select value={query.get('sort')||'updated'} onChange={e=>change('sort',e.target.value)}>{[['updated','Recently updated'],['title','Title'],['maturity','Maturity'],['due','Due date'],['priority','Priority']].map(([k,v])=><option key={k} value={k}>{v}</option>)}</select></Field>
  {!external&&<><Field label="Group register"><select value={query.get('group')||''} onChange={e=>change('group',e.target.value)}><option value="">No grouping</option>{['product','category','maturity'].map(v=><option key={v} value={v}>{v[0].toUpperCase()+v.slice(1)}</option>)}</select></Field><label className="check"><input type="checkbox" checked={query.get('mine')==='true'} onChange={e=>change('mine',e.target.checked?'true':'')}/>My owned ideas and actions</label></>}
 </div>;
}

export function GroupedIdeas({rows,group,render}:{rows:any[];group:string;render:(r:any[])=>any}){
 if(!['product','category','maturity'].includes(group))return render(rows);
 const groups=new Map<string,any[]>();for(const r of rows){const name=group==='maturity'?`M${r.maturity} ${r.maturity_name}`:r.data[group]||'Unassigned';groups.set(name,[...(groups.get(name)||[]),r]);}
 return <>{[...groups].map(([name,items])=><Section key={name} title={name}>{render(items)}</Section>)}</>;
}

export function ReportControls({query,change}:{query:URLSearchParams;change:(k:string,v:string)=>void}){
 return <div className="filters"><Field label="Reporting from"><input type="date" value={query.get('report_start')||''} onChange={e=>change('report_start',e.target.value)}/></Field><Field label="Reporting through"><input type="date" value={query.get('report_end')||''} onChange={e=>change('report_end',e.target.value)}/></Field><Field label="Product"><input value={query.get('product')||''} onChange={e=>change('product',e.target.value)}/></Field><Field label="Plant"><input value={query.get('plant')||''} onChange={e=>change('plant',e.target.value)}/></Field></div>;
}

export function ReportView({report:r}:{report:RecordData}){
 const [type,setType]=useState('Cost reduction'),[metric,setMetric]=useState('approved_forecast');
 const t=r.totals[type],applications=r.applications.filter((a:any)=>a.value_type===type),nonfinancial=['Capacity','Nonfinancial'].includes(type);
 const definitions=[['opportunity','Unweighted opportunity'],['approved_forecast','Approved forecast'],['implemented','Implemented benefit'],['verified','Verified actual']];
 return <>
  <div className="report-context"><span className="eyebrow">PROGRAM PERFORMANCE</span><h2>From opportunity to verified value</h2><p>{r.currency} · {dateText(r.start)} – {dateText(r.end)} · {r.scope}{r.filters?.product?' · Product '+r.filters.product:''}{r.filters?.plant?' · Plant '+r.filters.plant:''}</p><small>Refreshed {dateText(r.as_of,true)} · {r.fx_basis}</small></div>
  <Field label="Reported value type"><select value={type} onChange={e=>setType(e.target.value)}>{Object.keys(r.totals).map(v=><option key={v}>{v}</option>)}</select></Field>
  <p>In-year net recurring benefit. Annual run rate and one-time cash spend remain separate. {nonfinancial?'This value type has a separate operational metric.':''}</p>
  <div className="metrics">{definitions.map(([key,name])=><button key={key} className={'metric metric-link '+(metric===key?'selected':'')} onClick={()=>{setMetric(key);document.getElementById('supporting-applications')?.scrollIntoView({behavior:'smooth',block:'start'});}}><span>{name}</span><strong>{nonfinancial?'Separate metric':money(t[key],r.currency)}</strong><small>{key==='opportunity'&&t.unknown_applications?`${t.unknown_applications} application(s) still unquantified`:'Open contributing applications ↓'}</small></button>)}</div>
  <div className="target-strip"><div><span>Target for this metric, scope and period</span><strong>{money(r.targets[type].target,r.currency)}</strong></div><div><span>Approved one-time cash spend</span><strong>{nonfinancial?'Separate metric':money(t.spend,r.currency)}</strong></div><p>{r.target_scope}. Parent allocations and additional targets are distinguished.</p></div>
  <Section title="Supporting applications and reconciliation"><div id="supporting-applications" className="report-anchor"><p>Included and excluded applications for <strong>{type}</strong> · {definitions.find(([k])=>k===metric)?.[1]}. Select an idea for comparable unit costs, monthly calculations and approval history.</p><div className="table-scroll"><table><thead><tr><th>Idea / application</th><th>Product / part / plant</th><th>Approved forecast</th><th>Actual / verified</th><th>Observation coverage</th><th>Snapshot and exclusions</th></tr></thead><tbody>{applications.map((a:any)=><tr key={a.idea_id+a.application_id}><td><Link to={'/vave/ideas/'+a.idea_id}>{a.reference} · {a.scope}</Link></td><td>{a.product} / {a.part} / {a.plant}</td><td>{money(a.approved_forecast,r.currency)}<small>{a.currency} × {a.fx_rate}</small></td><td>{money(a.actual,r.currency)} / {money(a.verified,r.currency)}</td><td>{a.reported_periods} reported, {a.verified_periods} verified / {a.eligible_periods} eligible</td><td>{a.forecast_version?dateText(a.forecast_version,true):'No approved financial snapshot'}<small>{a.excluded||'Selected application'}</small></td></tr>)}</tbody></table></div>{!applications.length&&<p>No applications of this type.</p>}</div></Section>
  <Section title="Targets and allocation"><div className="table-scroll"><table><thead><tr><th>Scope</th><th>Metric / type</th><th>Period</th><th>Target</th><th>Allocation</th></tr></thead><tbody>{r.target_definitions.map((t:any,n:number)=><tr key={n}><td>{t.scope}</td><td>{t.metric}<small>{t.value_type}</small></td><td>{dateText(t.start)} – {dateText(t.end)}</td><td>{money(t.amount,r.currency)}</td><td>{t.scope==='Program'?'Parent total':t.additional?'Additional target':'Allocated from parent'}</td></tr>)}</tbody></table></div></Section>
  <Section title="Maturity and cohort conversion"><p>{r.cohort.definition} · {r.cohort.submissions} submissions. Current maturity counts differ from cumulative attainment.</p><div className="table-scroll"><table><thead><tr><th>Maturity</th><th>Current count</th><th>Submission cohort attained</th></tr></thead><tbody>{r.distribution.map((d:any)=><tr key={d.maturity}><td>M{d.maturity} {d.name}</td><td>{d.count}</td><td>{d.maturity?r.cohort.attained[d.maturity-1]:r.cohort.submissions}</td></tr>)}</tbody></table></div><details><summary>Recorded gate durations</summary>{r.gate_times.map((g:any,n:number)=><p key={n}><Link to={'/vave/ideas/'+g.idea_id}>Open contributing idea</Link> · M{g.maturity} · {g.days} calendar days since preceding gate</p>)}</details></Section>
 </>;
}

export function VaveWork(){
 const [work,setWork]=useState<RecordData|null>(null),[error,setError]=useState('');useEffect(()=>{api('/vave/work').then(setWork).catch(e=>setError(e.message));},[]);
 const lists:Record<string,string>={owned:'My ideas',actions:'My implementation actions',reviews:'My gate reviews',screening:'Screening assignments'};
 return <><span className="eyebrow">ACCOUNTABILITY AND DECISIONS</span><h1>My VAVE work</h1><p>Owned ideas, actions and pending gate decisions across your authorized programs.</p><ErrorBox error={error}/>{work&&Object.entries(lists).map(([key,title])=><Section key={key} title={title}>{!work[key].length&&<p>Nothing outstanding.</p>}{work[key].map((r:any,n:number)=><div className="vave-row" key={r.id+n}><Link to={'/vave/ideas/'+r.id}>{r.reference} · {r.title}</Link><p>{r.program} · {r.action?r.action.title:r.role?`M${r.gate} ${r.role} review`:r.next_action||'Next action needed'} · Due {dateText(r.action?.due_date||r.due_date)}</p>{r.missing?.length>0&&<small>{r.missing.join('; ')}</small>}</div>)}</Section>)}</>;
}

export function NoticePreferences(){
 const [prefs,setPrefs]=useState<RecordData|null>(null),[error,setError]=useState('');useEffect(()=>{api('/vave/preferences').then(setPrefs).catch(e=>setError(e.message));},[]);
 return <><ErrorBox error={error}/>{prefs&&<label className="check"><input type="checkbox" checked={prefs.data.routine_notices!==false} onChange={async e=>{try{setPrefs(await send('/vave/preferences',{record_version:prefs.record_version,data:{...prefs.data,routine_notices:e.target.checked}},'PUT'));}catch(e){setError((e as Error).message);}}}/>Show routine approaching-deadline notices. Mandatory decisions and overdue notices remain visible.</label>}</>;
}

export function LegacyEvidence({id}:{id:string}){
 const [record,setRecord]=useState<RecordData|null>(null),[error,setError]=useState('');useEffect(()=>{api('/vave/ideas/'+id+'/legacy').then(setRecord).catch(e=>setError(e.message));},[id]);
 return <Section title="Prior IdeaFlow evidence"><ErrorBox error={error}/>{record&&<><p>The existing evaluation idea was adapted on {dateText(record.adapted_at,true)}. Its identity and prior records remain retained. Earlier values and approvals describe the former test case and do not count as VAVE approvals or benefits.</p><h3>{record.idea.reference} · {record.idea.title}</h3><p>{record.idea.problem}</p><p>Prior lifecycle: {record.idea.stage} · {record.idea.disposition}</p><p>{record.reason}</p>{record.plans&&<details><summary>{record.plans.length} retained financial versions · {record.periods.length} plan periods · {record.actuals.length} recorded results</summary><pre className="json-preview">{JSON.stringify({plans:record.plans,periods:record.periods,actuals:record.actuals},null,2)}</pre></details>}<h3>Prior actions and discussion</h3>{record.tasks.map((t:any)=><p key={t.id}>{t.title} · {t.status}</p>)}{record.comments.map((c:any)=><p key={c.id}>{c.body}</p>)}</>}</Section>;
}
