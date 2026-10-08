from collections import defaultdict, Counter
from statistics import median
from math import ceil
from .domain import STAGES, LIFECYCLE

def days(a,b): return max(0,(b-a).total_seconds()/86400)
def distribution(values):
    values=sorted(values)
    return {'count':len(values),'median':median(values) if values else None,'p90':values[max(0,ceil(len(values)*.9)-1)] if values else None,'small_sample':len(values)<5}

def discover(ideas,events,as_of,basis='calendar',completed_only=False):
    traces=defaultdict(list)
    for e in sorted(events,key=lambda e:(e.occurred_at,e.sequence,e.id)):
        if e.event_type in LIFECYCLE and e.occurred_at<=as_of: traces[e.idea_id].append(e)
    edges=defaultdict(lambda:{'count':0,'cases':set(),'durations':[]})
    variants=defaultdict(lambda:{'cases':[],'durations':[],'complete':False})
    visits=[];rework=[];corrections=[];throughput=Counter();cycle=[];selected=[]
    for idea in ideas:
        trace=traces[idea.id]
        if not trace: continue
        final=trace[-1];complete=final.to_stage=='Realized' and final.to_disposition not in ('Rejected','Cancelled')
        if completed_only and not complete: continue
        selected.append(idea)
        terminal=final.to_disposition in ('Rejected','Cancelled')
        chain=[('Start',trace[0].occurred_at)]+[(e.activity,e.occurred_at) for e in trace]+[(('End' if complete or terminal else 'In progress'),trace[-1].occurred_at if complete or terminal else as_of)]
        for (a,ta),(b,tb) in zip(chain,chain[1:]):
            edge=edges[a,b];edge['count']+=1;edge['cases'].add(idea.id);edge['durations'].append(days(ta,tb))
        backward=False; correction=False;entry=None;stage=None;held_at=None;hold=0;case_hold=0;first_realized=None
        for e in trace:
            if e.event_type in ('CREATED','STAGE_CHANGED','REJECTED','CANCELLED'):
                if entry is not None:
                    extra=days(held_at,e.occurred_at) if held_at else 0
                    calendar=days(entry,e.occurred_at)
                    visits.append({'idea_id':idea.id,'stage':stage,'calendar_days':calendar,'hold_days':hold+extra,'active_days':max(0,calendar-hold-extra),'completed':True})
                    case_hold+=hold+extra
                entry=None if e.event_type in ('REJECTED','CANCELLED') or e.to_stage=='Realized' else e.occurred_at
                stage=e.to_stage;hold=0;held_at=None
                if e.event_type=='STAGE_CHANGED' and e.from_stage in STAGES and STAGES.index(e.to_stage)<STAGES.index(e.from_stage):
                    backward=True
                    if e.from_stage=='Realized': correction=True
                if e.to_stage=='Realized' and first_realized is None: first_realized=e.occurred_at
            elif e.event_type=='HELD': held_at=e.occurred_at
            elif e.event_type=='RESUMED' and held_at:
                hold+=days(held_at,e.occurred_at);held_at=None
        if entry is not None:
            extra=days(held_at,as_of) if held_at else 0;calendar=days(entry,as_of)
            visits.append({'idea_id':idea.id,'stage':stage,'calendar_days':calendar,'hold_days':hold+extra,'active_days':max(0,calendar-hold-extra),'completed':False,'on_hold_days':extra,
                'overdue':bool(idea.expected_finish and idea.expected_finish<as_of.date())})
        if backward: rework.append(idea.id)
        if correction: corrections.append(idea.id)
        duration=days(trace[0].occurred_at,first_realized) if first_realized else None
        if duration is not None and basis=='active': duration=max(0,duration-case_hold)
        if complete:
            throughput[first_realized.strftime('%Y-%m')]+=1;cycle.append(duration)
        key=tuple(e.activity for e in trace)
        v=variants[key,complete];v['cases'].append(idea.id);v['complete']=complete
        if complete: v['durations'].append(duration)
    stage_rows=[]
    for stage in STAGES:
        closed=[v for v in visits if v['stage']==stage and v['completed']]
        opened=[v for v in visits if v['stage']==stage and not v['completed']]
        stage_rows.append({'stage':stage,**distribution(v[basis+'_days'] for v in closed),'open_count':len(opened),
            'oldest_active_days':max((v['active_days'] for v in opened),default=None),'overdue_count':sum(v['overdue'] for v in opened),
            'held_over_30':sum(v['on_hold_days']>30 for v in opened),'idea_ids':list({v['idea_id'] for v in closed+opened}),
            'repeated_visits':len(closed+opened)-len({v['idea_id'] for v in closed+opened})})
    return {'as_of':as_of,'basis':basis,'case_count':len(selected),'completed_only':completed_only,
        'edges':[{'source':a,'target':b,'traversals':e['count'],'case_count':len(e['cases']),'median_days':median(e['durations']),'idea_ids':sorted(e['cases'])} for (a,b),e in edges.items()],
        'stages':stage_rows,'visits':visits,'variants':[{'path':list(path),'case_count':len(v['cases']),'share':len(v['cases'])/len(selected) if selected else 0,
        'completed':complete,'median_completed_days':median(v['durations']) if v['durations'] else None,'idea_ids':v['cases']} for (path,complete),v in sorted(variants.items(),key=lambda kv:-len(kv[1]['cases']))],
        'rework':{'numerator':len(rework),'denominator':len(selected),'idea_ids':rework,'correction_ids':corrections},
        'throughput':[{'month':m,'count':n} for m,n in sorted(throughput.items())],'completed_cycle':distribution(cycle)}
