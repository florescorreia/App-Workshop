import {useEffect,useState} from 'react';
import {useSearchParams} from 'react-router-dom';
import {api,money,dateText,RecordData} from './api';
import {Chart,ErrorBox,Field,Section} from './components';

function nextMonth(month:string){const d=new Date(month+'T12:00:00Z');d.setUTCMonth(d.getUTCMonth()+1);return d.toISOString().slice(0,10);}

export function FinancialEvidence({idea}:{idea:RecordData}){
 const [params,setParams]=useSearchParams(),base=idea.financials;
 const start=params.get('value_start')||base.start,end=params.get('value_end')||base.end;
 const [range,setRange]=useState({start:start.slice(0,7),end:end.slice(0,7)}),[data,setData]=useState<RecordData|null>(null),[error,setError]=useState('');
 useEffect(()=>setRange({start:start.slice(0,7),end:end.slice(0,7)}),[start,end]);
 useEffect(()=>{
  let live=true;setError('');setData(null);
  if(!params.get('value_start')&&!params.get('value_end')){setData(base);return;}
  api('/ideas/'+idea.id+'/value?'+new URLSearchParams({start,end})).then(d=>{if(live)setData(d);}).catch(e=>{if(live)setError(e.message);});
  return()=>{live=false;};
 },[idea.id,idea.record_version,start,end,params.get('value_start'),params.get('value_end')]);
 function apply(e:React.FormEvent){
  e.preventDefault();setError('');
  if(range.end<range.start){setError('Through month must be on or after From month.');return;}
  const count=(Number(range.end.slice(0,4))-Number(range.start.slice(0,4)))*12+Number(range.end.slice(5))-Number(range.start.slice(5))+1;
  if(count>120){setError('Choose a range of at most 120 months.');return;}
  const p=new URLSearchParams(params);p.set('value_start',range.start+'-01');p.set('value_end',range.end+'-01');setParams(p,{replace:true});
 }
 function reset(){const p=new URLSearchParams(params);p.delete('value_start');p.delete('value_end');setError('');setParams(p,{replace:true});setRange({start:base.start.slice(0,7),end:base.end.slice(0,7)});}
 const labels=['Approved expected','Reported actual','Verified'];
 return <Section title="Cumulative value evidence" note="Calculated from the approved monthly plan and saved outcomes. There are no amounts to enter here.">
  <p>The full idea timeline covers the current approved schedule (or latest saved draft before approval) and recorded outcome months. Without either, it uses the idea's dates. Benefits can continue after implementation finishes.</p>
  <form className="filters" onSubmit={apply}><Field label="Evidence from month"><input type="month" required value={range.start} onChange={e=>setRange({...range,start:e.target.value})}/></Field><Field label="Evidence through month"><input type="month" required value={range.end} onChange={e=>setRange({...range,end:e.target.value})}/></Field><button className="primary">Apply date range</button><button type="button" onClick={reset}>Full idea timeline</button></form>
  <ErrorBox error={error}/>{data?<>
   <p className="as-of">Showing {dateText(data.start)} – {dateText(data.end)} · Evidence as of {dateText(data.as_of,true)}</p>
   {!idea.plans.some((p:any)=>p.status==='Approved')&&<p className="financial-note">No valid approved plan yet. Draft amounts do not appear as expected value. Save and approve the monthly plan when the business case is ready.</p>}
   {base.idea_timeline.clipped&&<p>The recorded timeline exceeds 120 months. The default shows its latest 120 months; choose a shorter range to inspect earlier periods.</p>}
   <Chart title="Cumulative expected, actual and verified net benefit" xRange={[data.start,nextMonth(data.end)]} data={['expected','actual','verified'].map((k,i)=>({type:'scatter',mode:'lines+markers',name:labels[i],x:data.series.map((s:any)=>s.month),y:data.series.map((s:any)=>s['cumulative_'+k]),connectgaps:false,line:{color:['#278c83','#486cb5','#bd842c'][i]}}))}/>
   <p>Cumulative means the running total from the selected From month. Net benefit is gross benefit minus recurring cost; implementation spend is separate. Missing or unverified months remain gaps, including current and future actuals. Changing the dates only changes this view.</p>
   <p>{data.coverage.reported} of {data.coverage.eligible} eligible approved-plan months reported · {data.coverage.verified} verified. Risk-adjusted expected benefit uses probability alone. ROI = (net benefit − implementation spend) / implementation spend × 100.</p>
   <div className="table-scroll"><table aria-label="Monthly and cumulative value evidence"><thead><tr><th>Month</th><th>Expected net</th><th>Actual net</th><th>Verified net</th><th>Cumulative expected</th><th>Cumulative actual</th><th>Cumulative verified</th></tr></thead><tbody>{data.series.map((s:any)=><tr key={s.month}><td>{dateText(s.month)}</td>{['expected','actual','verified','cumulative_expected','cumulative_actual','cumulative_verified'].map(k=><td key={k}>{money(s[k])}</td>)}</tr>)}</tbody></table></div>
  </>:!error&&<p className="loading">Loading value evidence…</p>}
 </Section>;
}
