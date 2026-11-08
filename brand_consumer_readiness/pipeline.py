"""Brand approval, consumer journey readiness, and experiment-linked review controls."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
GATES=('brand_approved','content_approved','capacity_confirmed','referral_path_tested','tracking_validated','partner_deliverables_agreed','family_experience_reviewed','budget_approved')

def launch_status(row):
    missing=[g for g in GATES if str(row.get(g,'')).lower()!='yes']
    try:
        slots=int(row['available_slots'])
        expected=int(row['expected_responses'])
        if slots<0 or expected<0: raise ValueError('negative volumes')
    except (ValueError, KeyError):
        return 'HOLD',missing+['valid_capacity_inputs']
    if slots<expected: missing.append('capacity_shortfall')
    return ('HOLD' if missing else 'READY'),missing

def contribution_scenarios(conversion_difference, assigned, margin, contact_cost, revenue_per_conversion):
    if min(assigned,margin,contact_cost,revenue_per_conversion)<0 or margin>1: raise ValueError('invalid assumption')
    incremental=conversion_difference*assigned
    contribution=incremental*revenue_per_conversion*margin-assigned*contact_cost
    return {'incremental_conversions':incremental,'incremental_contribution':contribution,'roi':None if contact_cost==0 else contribution/(assigned*contact_cost)}

def main():
    out=ROOT/'results';out.mkdir(exist_ok=True)
    with (ROOT/'templates/launch_review.csv').open() as f: inputs=list(csv.DictReader(f))
    checks=[dict(program=r['program'],status=launch_status(r)[0],open_items=', '.join(launch_status(r)[1])) for r in inputs]
    with (out/'launch_review.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['program','status','open_items'],lineterminator='\n');writer.writeheader();writer.writerows(checks)
    with (ROOT.parent/'campaign_experiments/results/assigned_arm_metrics.csv').open() as f: arms=list(csv.DictReader(f))
    control=next(r for r in arms if r['segment']=='No E-Mail')
    treated=next(r for r in arms if r['segment']=='Mens E-Mail')
    difference=int(treated['conversions'])/int(treated['assigned'])-int(control['conversions'])/int(control['assigned'])
    scenarios=[]
    for margin in (.2,.3,.4):
        scenarios.append(dict(margin=margin,assumed_contact_cost=.01,assumed_revenue_per_conversion=25,**contribution_scenarios(difference,10000,margin,.01,25)))
    with (out/'budget_sensitivity.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(scenarios[0]),lineterminator='\n');writer.writeheader();writer.writerows(scenarios)
    result={'source':'../campaign_experiments/results/assigned_arm_metrics.csv','assigned_records':sum(int(a['assigned']) for a in arms),'conversion_difference_percentage_points':100*difference,'gates':len(GATES),'reviewed_program_fixtures':len(inputs),'ready_fixture_programs':sum(r['status']=='READY' for r in checks),'held_fixture_programs':sum(r['status']=='HOLD' for r in checks),'scope':'Randomized email campaign evaluation linked with eight-gate launch readiness and contribution margin sensitivity.'}
    (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
