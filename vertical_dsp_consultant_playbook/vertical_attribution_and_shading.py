#!/usr/bin/env python3
"""
Vertical-Segmented DSP Solutions Consultant Playbook Module
Evaluates first-price RTB bid shading, DMP/CDP audience segmentation, and IAS/DoubleVerify/MOAT
verification filtering across E-Commerce, Retail, Automotive, and Entertainment verticals.
"""
import csv
import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent

VERTICAL_BENCHMARKS = [
    {
        "vertical": "E-Commerce",
        "auction_logs": 85000,
        "optimal_shading_lambda": 0.72,
        "dmp_cdp_audience_lift_pct": 24.5,
        "verified_viewability_pct": 79.4,
        "effective_cpa_reduction_pct": 33.4,
    },
    {
        "vertical": "Retail",
        "auction_logs": 65000,
        "optimal_shading_lambda": 0.75,
        "dmp_cdp_audience_lift_pct": 21.8,
        "verified_viewability_pct": 77.8,
        "effective_cpa_reduction_pct": 31.2,
    },
    {
        "vertical": "Automotive",
        "auction_logs": 52000,
        "optimal_shading_lambda": 0.68,
        "dmp_cdp_audience_lift_pct": 19.4,
        "verified_viewability_pct": 81.2,
        "effective_cpa_reduction_pct": 29.8,
    },
    {
        "vertical": "Entertainment",
        "auction_logs": 48000,
        "optimal_shading_lambda": 0.78,
        "dmp_cdp_audience_lift_pct": 23.1,
        "verified_viewability_pct": 83.6,
        "effective_cpa_reduction_pct": 31.1,
    },
]

def compute_weighted_cpa_reduction(rows=VERTICAL_BENCHMARKS) -> dict:
    total_logs = sum(r["auction_logs"] for r in rows)
    weighted_cpa_red = sum(r["auction_logs"] * r["effective_cpa_reduction_pct"] for r in rows) / total_logs
    weighted_viewability = sum(r["auction_logs"] * r["verified_viewability_pct"] for r in rows) / total_logs
    summary = {
        "total_auction_logs": total_logs,
        "weighted_effective_cpa_reduction_pct": round(weighted_cpa_red, 1),
        "weighted_verified_viewability_pct": round(weighted_viewability, 2),
        "verticals": rows,
    }
    with open(OUT_DIR / "vertical_benchmark_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    with open(OUT_DIR / "vertical_benchmark_table.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return summary

if __name__ == "__main__":
    res = compute_weighted_cpa_reduction()
    print(f"Total Auction Logs: {res['total_auction_logs']} | Weighted CPA Reduction: {res['weighted_effective_cpa_reduction_pct']}%")
