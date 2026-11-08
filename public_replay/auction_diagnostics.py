#!/usr/bin/env python3
"""Reproducible, budget-constrained replay of the authors' iPinYou sample.

Only Python's standard library is required. The supplied pCTR is an upstream
model output; this module does not retrain or independently validate that model.
"""
import argparse
import csv
import hashlib
import json
import math
import sqlite3
import urllib.request
from pathlib import Path

UPSTREAM = "56f8aea7b9f67eaf6d8d731fc091016f22f2739d"
BASE = f"https://raw.githubusercontent.com/wnzhang/rtbcontrol/{UPSTREAM}/exp-data"
GRID = (10, 20, 30, 40, 50, 70, 90, 120, 150, 200, 250, 300)
EXPECTED_HASHES = {"train": "db0ecc0f49626993a2bbadab0561ddb3307926abc161f823e07b707c10aacefd",
                   "test": "ba3dc59962ec8f58ffb0ca3de5c833d4b589fc7215857f4ad7beb92726f24798"}


def load_rows(path):
    rows = []
    with Path(path).open() as stream:
        for number, fields in enumerate(csv.reader(stream, delimiter="\t"), 1):
            if len(fields) != 4:
                raise ValueError(f"{path}:{number}: expected four fields")
            click, price, pctr, exchange = int(fields[0]), int(fields[1]), float(fields[2]), fields[3]
            if click not in (0, 1) or price < 0 or not math.isfinite(pctr) or not 0 <= pctr <= 1:
                raise ValueError(f"{path}:{number}: invalid click, price or pCTR")
            rows.append((click, price, pctr, exchange))
    if not rows:
        raise ValueError("Empty auction sample")
    return rows


def replay(rows, base_bid, mean_ctr, budget, linear=True, pacing=False):
    if mean_ctr <= 0 or budget < 0:
        raise ValueError("Positive training mean CTR and nonnegative budget required")
    spend = wins = clicks = 0
    expected_clicks = 0.0
    for index, (click, price, pctr, _) in enumerate(rows):
        multiplier = 1.0
        if pacing:
            # Request-order pacing proxy. These samples contain no timestamps.
            target = budget * (index + 1) / len(rows)
            multiplier = max(0.25, min(2.0, 1.0 + (target - spend) / max(budget * 0.05, 1)))
        bid = min(300.0, base_bid * (pctr / mean_ctr if linear else 1) * multiplier)
        # Logged second-price replay, strict win rule; never charge the bid itself.
        if bid > price and spend + price <= budget:
            spend += price
            wins += 1
            clicks += click
            expected_clicks += pctr
    return {"base_bid": base_bid, "budget_units": budget, "spend_units": spend,
            "wins": wins, "clicks": clicks, "expected_clicks": round(expected_clicks, 6),
            "win_rate": wins / len(rows), "budget_utilization": spend / budget if budget else 0,
            "cost_per_click_units": spend / clicks if clicks else None}


def select_bid(train, mean_ctr, budget):
    trials = [replay(train, bid, mean_ctr, budget) for bid in GRID]
    # Only the upstream TRAIN split selects the parameter; test labels are never read here.
    best = max(trials, key=lambda r: (r["clicks"], -r["spend_units"], -r["base_bid"]))
    return best["base_bid"], trials


def run(data_dir, output_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    provenance = {}
    samples = {}
    for split in ("train", "test"):
        path = data_dir / f"{split}.txt"
        if not path.exists():
            urllib.request.urlretrieve(f"{BASE}/{split}.txt", path)
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != EXPECTED_HASHES[split]:
            raise ValueError(f"Unexpected {split} dataset hash; inspect provenance before running")
        samples[split] = load_rows(path)
        provenance[split] = {"url": f"{BASE}/{split}.txt", "sha256": hashlib.sha256(raw).hexdigest(),
                             "rows": len(samples[split]), "bytes": len(raw)}
    train, test = samples["train"], samples["test"]
    mean_ctr = sum(r[0] for r in train) / len(train)
    train_budget = sum(r[1] for r in train) // 2
    test_budget = sum(r[1] for r in test) // 2
    selected, trials = select_bid(train, mean_ctr, train_budget)
    baseline = replay(test, 90, mean_ctr, test_budget, linear=False)
    tuned = replay(test, selected, mean_ctr, test_budget)
    paced = replay(test, selected, mean_ctr, test_budget, pacing=True)
    db = sqlite3.connect(output_dir / "auctions.sqlite")
    db.execute("DROP TABLE IF EXISTS auctions")
    db.execute("CREATE TABLE auctions(split TEXT, row_id INTEGER, click INTEGER CHECK(click IN (0,1)), market_price INTEGER CHECK(market_price>=0), pctr REAL CHECK(pctr>=0 AND pctr<=1), exchange TEXT, PRIMARY KEY(split,row_id))")
    for split, rows in samples.items():
        db.executemany("INSERT INTO auctions VALUES(?,?,?,?,?,?)", ((split, i + 1, *row) for i, row in enumerate(rows)))
    db.commit()
    query = """WITH buckets AS (
        SELECT split, CAST((row_id-1)/10000 AS INTEGER) AS request_bucket,
          COUNT(*) AS opportunities, SUM(click) AS clicks,
          AVG(pctr) AS mean_pctr, AVG(market_price) AS mean_market_price
        FROM auctions GROUP BY split, request_bucket)
        SELECT *, 1.0*clicks/opportunities AS observed_ctr FROM buckets
        ORDER BY split, request_bucket"""
    cur = db.execute(query)
    with (output_dir / "request_bucket_diagnostics.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow([d[0] for d in cur.description])
        writer.writerows(cur)
    counts = dict(db.execute("SELECT split,COUNT(*) FROM auctions GROUP BY split"))
    integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    db.close()
    with (output_dir / "training_sweep.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(trials[0]))
        writer.writeheader()
        writer.writerows(trials)
    summary = {"dataset": "Authors' iPinYou campaign 1458 sample", "upstream_commit": UPSTREAM,
        "provenance": provenance, "training_mean_ctr": mean_ctr,
        "selection": "Maximum TRAIN replay clicks; ties prefer lower spend, then lower base bid",
        "selected_base_bid": selected, "holdout_constant_90": baseline,
        "holdout_train_selected_linear": tuned, "holdout_request_order_pacing": paced,
        "row_counts_sql": counts, "sqlite_integrity": integrity,
        "click_delta_vs_constant": tuned["clicks"] - baseline["clicks"],
        "replay_cpc_reduction_pct": round((1 - tuned["cost_per_click_units"] / baseline["cost_per_click_units"]) * 100, 4)}
    (output_dir / "validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "results")
    args = parser.parse_args()
    run(args.data_dir, args.output_dir)
