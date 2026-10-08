"""Read-only checks for the explicitly imported HarborWorks batch. Run in backend."""
import hashlib
import json
import os
from collections import Counter
from decimal import Decimal as D
from datetime import datetime, time, timezone

import httpx
from sqlalchemy import select, text
from app.db import SessionLocal, now
from app.models import Idea, IdeaEvent, DemoBatch, FinancialPlan, PlanPeriod, ValuePeriod, Task, Comment
from app.domain import STAGES, LIFECYCLE, EDGES
from app.financial import app_today, add_month
from app.restore_check import fingerprints
from sqlalchemy import create_engine

KEY = 'harborworks-demo-v1'


def number(value):
    return D(str(value)) if value is not None else None


def main():
    engine = create_engine(os.environ['DATABASE_ADMIN_URL'])
    baseline = json.load(open('/handover/harborworks-after.json'))
    assert fingerprints(engine) == baseline, 'Business data changed after import'
    with SessionLocal() as db, httpx.Client(base_url='http://localhost:8000/api/v1', timeout=30) as client:
        login = client.post('/session/login', json={'email': os.environ['ADMIN_EMAIL'], 'password': os.environ['ADMIN_PASSWORD']})
        login.raise_for_status()
        batch = db.scalar(select(DemoBatch).where(DemoBatch.batch_key == KEY))
        assert batch and batch.seed == 42 and batch.anchor_date == app_today()
        ideas = list(db.scalars(select(Idea).where(Idea.demo_batch_id == batch.id)))
        ids = {i.id for i in ideas}
        events = list(db.scalars(select(IdeaEvent).where(IdeaEvent.idea_id.in_(ids))))
        plans = list(db.scalars(select(FinancialPlan).where(FinancialPlan.idea_id.in_(ids))))
        approved = {p.idea_id: p for p in plans if p.status == 'Approved'}
        periods = list(db.scalars(select(PlanPeriod).where(PlanPeriod.plan_id.in_([p.id for p in approved.values()]))))
        results = list(db.scalars(select(ValuePeriod).where(ValuePeriod.idea_id.in_(ids))))
        task_count = len(list(db.scalars(select(Task).where(Task.idea_id.in_(ids)))))
        comments = len(list(db.scalars(select(Comment).where(Comment.idea_id.in_(ids)))))
        assert len(ideas) == 60 and len(events) == batch.counts['events'] and len(results) == batch.counts['value_periods']
        assert task_count == batch.counts['tasks'] and comments == 60
        assert set(i.stage for i in ideas) == set(STAGES)
        anchor = datetime.combine(batch.anchor_date, time(12), timezone.utc)
        assert all(add_month(batch.anchor_date.replace(day=1), -18) <= i.created_at.date() <= batch.anchor_date for i in ideas)
        assert all(e.occurred_at <= anchor and e.occurred_at <= now() and e.recorded_at >= e.occurred_at for e in events)
        assert all(e.provenance['fictional'] and e.provenance['batch_key'] == KEY for e in events)
        assert all(r.month < app_today().replace(day=1) for r in results)
        for idea in ideas:
            ordered = sorted([e for e in events if e.idea_id == idea.id], key=lambda e: (e.occurred_at, e.sequence, e.id))
            assert [e.sequence for e in ordered] == list(range(1, len(ordered) + 1))
            trace = [e for e in ordered if e.event_type in LIFECYCLE]
            assert trace[0].activity == 'New'
            assert (trace[-1].to_stage, trace[-1].to_disposition) == (idea.stage, idea.disposition)
            for e in trace:
                if e.event_type == 'STAGE_CHANGED':
                    assert (e.from_stage, e.to_stage) in EDGES and e.from_disposition == 'Active'
                elif e.event_type in ('HELD', 'RESUMED'):
                    assert e.to_stage == e.from_stage
            if STAGES.index(idea.stage) >= STAGES.index('Approved'):
                assert idea.id in approved
        stage_counts = Counter(i.stage for i in ideas)
        dispositions = Counter(i.disposition for i in ideas)
        sites = Counter(i.site_id for i in ideas)
        overdue = sum(i.disposition == 'Active' and i.stage != 'Realized' and i.expected_finish < app_today() for i in ideas)
        assert stage_counts['Realized'] == 12 and dispositions['On hold'] >= 5 and dispositions['Rejected'] == 6 and dispositions['Cancelled'] == 3 and overdue >= 6
        assert set(sites) == {'Tampa', 'Atlanta', 'Dallas'}

        def get(path):
            response = client.get(path)
            response.raise_for_status()
            return response.json()

        portfolio = get('/dashboards/portfolio')
        value = get('/dashboards/value')
        process = get('/dashboards/process')
        assert get('/ideas?page_size=100')['total'] == len(ideas)
        assert {s['stage']: s['count'] for s in portfolio['stages']} == dict(stage_counts)
        assert portfolio['overdue_count'] == overdue
        assert process['case_count'] == len(ideas) and process['rework']['numerator'] >= 8
        assert sum(v['case_count'] for v in process['variants']) == len(ideas)
        stages = {s['stage']: s for s in process['stages']}
        assert stages['Analysis']['count'] >= 5 and stages['Analysis']['median'] > max(s['median'] or 0 for s in process['stages'] if s['stage'] != 'Analysis')
        plan_ids = {p.id: p.idea_id for p in approved.values()}
        start, end = value['start'], value['end']
        included = [p for p in periods if start <= p.month.isoformat() <= end]
        eligible = [p for p in included if p.month < app_today().replace(day=1)]
        actual = [r for r in results if start <= r.month.isoformat() <= end and r.gross is not None and r.recurring is not None]
        verified = [r for r in actual if r.verified_at]
        actual_keys = {(r.idea_id, r.month) for r in actual}
        verified_keys = {(r.idea_id, r.month) for r in verified}
        expected_actual = [p for p in eligible if (plan_ids[p.plan_id], p.month) in actual_keys]
        expected_verified = [p for p in eligible if (plan_ids[p.plan_id], p.month) in verified_keys]
        assert value['coverage'] == {'eligible': len(eligible), 'reported': len(expected_actual), 'verified': len(expected_verified)}
        assert number(value['planned']['net_benefit']) == sum(p.gross - p.recurring for p in included)
        assert number(value['actual']['net_benefit']) == sum(r.gross - r.recurring for r in actual)
        assert number(value['verified']['net_benefit']) == sum(r.verified_gross - r.verified_recurring for r in verified)
        assert number(value['expected_reported_cohort']) == sum(p.gross - p.recurring for p in expected_actual)
        assert number(value['expected_verified_cohort']) == sum(p.gross - p.recurring for p in expected_verified)
        assert value['coverage']['verified'] < value['coverage']['reported'] < value['coverage']['eligible']
        assert any(v['actual'] is None and v['verified'] is None for v in value['variance'])
        assert any(s['actual'] is None for s in value['series'])
        spend = sum(p.spend for p in included)
        benefit = sum(p.gross - p.recurring for p in included)
        assert abs(number(value['planned']['roi']['value']) - (benefit - spend) / spend * 100) < D('0.000001')
        # Existing bootstrap Admin is unchanged; no existing ideas were present.
        admin_rows = db.execute(text("SELECT row_to_json(t)::text FROM app_user t WHERE role='Admin'")).scalars().all()
        admin_hash = hashlib.sha256('\n'.join(sorted(admin_rows)).encode()).hexdigest()
        assert admin_hash == json.load(open('/handover/harborworks-before.json'))['app_user']['sha256']
        heroes = []
        for idea in sorted(ideas, key=lambda i: i.external_key)[:5]:
            detail = get('/ideas/' + idea.id)
            heroes.append({k: detail[k] for k in ('id', 'reference', 'title', 'site', 'stage', 'disposition', 'annual_net_potential', 'results', 'financials')})
        freight = heroes[0]
        fp = approved[freight['id']]
        planned = {p.month: p for p in periods if p.plan_id == fp.id}
        benefit_months = [r for r in results if r.idea_id == freight['id'] and r.gross > 0]
        assert len(benefit_months) == 2 and all(r.gross < planned[r.month].gross for r in benefit_months)
        assert any(not r['verified_at'] for r in heroes[3]['results'])
        report = {'status': 'PASS', 'batch_key': KEY, 'anchor_date': batch.anchor_date, 'timezone': os.environ['APP_TIMEZONE'],
                  'counts': {**batch.counts, 'comments': comments, 'plans': len(plans), 'approved_plans': len(approved), 'plan_periods': len(periods), 'verified_periods': len(verified)},
                  'stages': dict(stage_counts), 'dispositions': dict(dispositions), 'sites': dict(sites), 'overdue_active': overdue,
                  'creation_range': [min(i.created_at for i in ideas), max(i.created_at for i in ideas)],
                  'process': {'variants': len(process['variants']), 'rework_cases': process['rework']['numerator'], 'stages': process['stages']},
                  'value': value, 'heroes': heroes,
                  'checks': ['chronology/provenance', 'event sequence/workflow/current-state replay', 'site/stage/disposition mix', 'elapsed actuals', 'independent monetary/cohort/ROI sums', 'missing results remain null', 'Analysis bottleneck/rework', 'hero states and unverified Finance period', 'bootstrap Admin unchanged']}
        json.dump(report, open('/handover/harborworks-verification.json', 'w'), default=str, indent=2)
        print(json.dumps({k: report[k] for k in ('status', 'counts', 'stages', 'dispositions', 'sites', 'overdue_active', 'checks')}, default=str, indent=2))
    assert fingerprints(engine) == baseline, 'Verification changed business data'
    print('Read-only verification business fingerprints unchanged: PASS')


if __name__ == '__main__':
    main()
