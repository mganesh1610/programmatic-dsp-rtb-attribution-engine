"""Historical randomized email campaign evaluation with SQL reconciliation."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sqlite3
import urllib.request

import numpy as np
import pandas as pd
from scipy.stats import chisquare, norm, t

ROOT = Path(__file__).resolve().parent
SOURCE_URL = "http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"
SOURCE_SHA256 = "0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece"
ARMS = ["No E-Mail", "Mens E-Mail", "Womens E-Mail"]


def difference_of_rates(success_a, n_a, success_b, n_b):
    if min(n_a,n_b) <= 0:
        raise ValueError("Both assigned groups must have observations")
    if not (0 <= success_a <= n_a and 0 <= success_b <= n_b):
        raise ValueError("Invalid conversion count")
    p_a,p_b=success_a/n_a,success_b/n_b
    delta=p_a-p_b
    z=1.95996398454
    def wilson(success,n):
        rate=success/n
        center=(rate+z*z/(2*n))/(1+z*z/n)
        half=z*math.sqrt(rate*(1-rate)/n+z*z/(4*n*n))/(1+z*z/n)
        return center-half,center+half
    low_a,high_a=wilson(success_a,n_a)
    low_b,high_b=wilson(success_b,n_b)
    interval=[delta-math.sqrt((p_a-low_a)**2+(high_b-p_b)**2),
              delta+math.sqrt((high_a-p_a)**2+(p_b-low_b)**2)]
    pooled=(success_a+success_b)/(n_a+n_b)
    se_null=math.sqrt(pooled*(1-pooled)*(1/n_a+1/n_b))
    p_value=float(2*norm.sf(abs(delta/se_null))) if se_null else 1.0
    return {"absolute_conversion_difference":delta,"approximate_95_ci":interval,
            "two_sided_p_value":p_value,"treatment_conversion_rate":p_a,"control_conversion_rate":p_b}


def holm_adjust(p_values):
    values=np.asarray(p_values,dtype=float)
    if not ((values >= 0) & (values <= 1)).all():
        raise ValueError("P values must be in [0,1]")
    order=np.argsort(values,kind="stable")
    adjusted=np.empty(len(values))
    running=0.0
    for rank,ix in enumerate(order):
        running=max(running,(len(values)-rank)*values[ix])
        adjusted[ix]=min(1.0,running)
    return adjusted.tolist()


def welch_mean_difference(a,b):
    a,b=np.asarray(a,dtype=float),np.asarray(b,dtype=float)
    variance_a,variance_b=a.var(ddof=1)/len(a),b.var(ddof=1)/len(b)
    variance=variance_a+variance_b
    dof=variance**2/(variance_a**2/(len(a)-1)+variance_b**2/(len(b)-1)) if variance else float("inf")
    delta=float(a.mean()-b.mean())
    half=float(t.ppf(.975,dof)*math.sqrt(variance))
    return {"mean_difference":delta,"approximate_95_ci":[delta-half,delta+half]}


def main():
    data=ROOT/"data/hillstrom.csv"
    data.parent.mkdir(parents=True,exist_ok=True)
    if not data.exists():
        with urllib.request.urlopen(SOURCE_URL,timeout=60) as response:
            data.write_bytes(response.read())
    source=data.read_bytes()
    if hashlib.sha256(source).hexdigest()!=SOURCE_SHA256:
        raise ValueError("Source hash mismatch")
    frame=pd.read_csv(data)
    expected=["recency","history_segment","history","mens","womens","zip_code","newbie","channel","segment","visit","conversion","spend"]
    if frame.columns.tolist()!=expected or len(frame)!=64000 or frame.isna().any().any():
        raise ValueError("Unexpected dataset schema")
    frame.insert(0,"source_row",np.arange(1,len(frame)+1))
    if set(frame.segment)!=set(ARMS):
        raise ValueError("Unexpected assignment arm")
    out=ROOT/"results"
    out.mkdir(exist_ok=True)
    db_path=out/"experiments.sqlite"
    if db_path.exists():
        db_path.unlink()
    with sqlite3.connect(db_path) as db:
        frame.to_sql("assigned_outcomes",db,index=False)
        db.execute("CREATE UNIQUE INDEX assigned_customer_key ON assigned_outcomes(source_row)")
        sql=pd.read_sql_query((ROOT/"analysis.sql").read_text(),db).set_index("segment")
        integrity=db.execute("PRAGMA integrity_check").fetchone()[0]
    grouped=frame.groupby("segment",sort=True).agg(assigned=("source_row","size"),conversions=("conversion","sum"),
                                                  visits=("visit","sum"),total_spend=("spend","sum"))
    checks={"source_rows":len(frame)==64000,"all_arm_rows_preserved":int(sql.assigned.sum())==64000,
            "unique_surrogate_key":frame.source_row.is_unique,"sql_assigned_counts":bool((sql.assigned==grouped.assigned).all()),
            "sql_conversions":bool((sql.conversions==grouped.conversions).all()),
            "sql_visits":bool((sql.visits==grouped.visits).all()),
            "sql_spend":bool(np.allclose(sql.total_spend,grouped.total_spend,rtol=0,atol=1e-7)),
            "binary_conversion_and_visit":all(set(frame[c])<={0,1} for c in ["conversion","visit"]),
            "nonnegative_spend":bool((frame.spend>=0).all()),"sqlite_integrity":integrity=="ok"}
    control=frame.loc[frame.segment=="No E-Mail"]
    contrasts=[]
    cost=.01
    contribution_margin=.30
    for arm in ARMS[1:]:
        treatment=frame.loc[frame.segment==arm]
        delta=difference_of_rates(int(treatment.conversion.sum()),len(treatment),int(control.conversion.sum()),len(control))
        spend=welch_mean_difference(treatment.spend,control.spend)
        balance={}
        for col in ["recency","history","mens","womens","newbie"]:
            pooled_sd=math.sqrt((treatment[col].var(ddof=1)+control[col].var(ddof=1))/2)
            balance[col]=float((treatment[col].mean()-control[col].mean())/pooled_sd) if pooled_sd else 0.0
        contrasts.append({"assigned_arm":arm,"treatment_n":len(treatment),"control_n":len(control),**delta,
                          "spend_per_assigned_customer":spend,"baseline_standardized_mean_differences":balance,
                          "scenario":{"contact_cost_assumption":cost,"contribution_margin_assumption":contribution_margin,
                                      "net_incremental_contribution_per_assigned":spend["mean_difference"]*contribution_margin-cost,
                                      "incremental_roi":(spend["mean_difference"]*contribution_margin-cost)/cost,
                                      "interpretation":"financial sensitivity using assumed costs and margin, not observed profit or retention"}})
    adjusted=holm_adjust([v["two_sided_p_value"] for v in contrasts])
    for row,p_value in zip(contrasts,adjusted):
        row["holm_adjusted_p_value"]=p_value
    assignment_chi=chisquare([len(frame.loc[frame.segment==arm]) for arm in ARMS])
    report={"source":{"url":SOURCE_URL,"sha256":SOURCE_SHA256,"rows":len(frame),"columns":expected,
                      "design":"three randomized email assignments, two-week observed outcome window"},
            "intent_to_treat":"All assigned customers retained. Do not condition on post-assignment visits.",
            "assignment_ratio":{"null":"equal three-arm assignment","chi_square":float(assignment_chi.statistic),
                                "p_value":float(assignment_chi.pvalue)},
            "contrasts":contrasts,"multiplicity":"Holm adjustment for two email-versus-control conversion tests; CIs are individual Wilson-Newcombe approximate 95% intervals",
            "checks":checks,"passed":sum(checks.values()),"failed":sum(not v for v in checks.values()),
            "boundary":"Historical retail email experiment. Not telecom churn, realized employer uplift, net profit or a new live campaign. Original source specifies no currency code."}
    if not all(checks.values()):
        raise AssertionError(checks)
    sql.to_csv(out/"assigned_arm_metrics.csv")
    (out/"validation.json").write_text(json.dumps(report,indent=2)+"\n")
    rows=[{"arm":v["assigned_arm"],"treatment_n":v["treatment_n"],"control_n":v["control_n"],
           "conversion_lift_pp":v["absolute_conversion_difference"]*100,
           "ci_low_pp":v["approximate_95_ci"][0]*100,"ci_high_pp":v["approximate_95_ci"][1]*100,
           "holm_p":v["holm_adjusted_p_value"]} for v in contrasts]
    pd.DataFrame(rows).to_csv(out/"contrast_results.csv",index=False)
    (out/"review.html").write_text("<!doctype html><html><meta charset='utf-8'><title>Campaign experiment review</title>"
        "<style>body{font:16px Arial;max-width:1000px;margin:40px auto;color:#20272c}td,th{padding:12px;text-align:right;border-bottom:1px solid #ddd}</style>"
        "<h1>Campaign experiment review</h1><p>64,000 historical randomized email assignments. Two-week conversion is the primary reported outcome. "
        "Both email arms are shown; all assigned customers remain in the denominator.</p>"+
        pd.DataFrame(rows).to_html(index=False,float_format=lambda n:f"{n:.4f}")+
        "<p>Intervals are individual approximate 95% CIs. P values use Holm adjustment across two comparisons. "
        "Profit and ROI require external cost and margin assumptions; see validation.json.</p></html>")
    print(json.dumps({"rows":len(frame),"contrasts":rows,"checks_passed":report["passed"]},indent=2))


if __name__=="__main__":
    main()
