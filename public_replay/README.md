# Public Auction Replay and Trading Desk Diagnostics

This module turns public auction samples into reproducible campaign diagnostics, a training-only parameter sweep, and an untouched test replay using Python's standard library.

## Run

```sh
python3 public_replay/auction_diagnostics.py
python3 -m unittest discover -s public_replay -p 'test_*.py' -v
```

The first command downloads 100,000 training and 100,000 test records pinned to upstream commit `56f8aea7b9f67eaf6d8d731fc091016f22f2739d`. Data stays local and is excluded from Git. SHA-256 hashes and observed row counts are recorded in `results/validation_summary.json`.

## Architecture and methods

Pinned TSV download → schema validation → SQLite load → SQL request-bucket diagnostics → TRAIN bid sweep → TEST policy comparison → stakeholder briefing.

Input columns: `click` (0/1), `market_price` (nonnegative integer in original price units), `pctr` (upstream predicted probability), and `exchange` (string). `split` and `row_id` are ingestion keys. No timestamps, campaign membership, conversion, viewability or identity fields are invented.

Linear bidding is `b_i = min(300, b0 * pCTR_i / CTR_train)`. Under a strict `bid > market_price` win rule, spend increases by the logged market price only if the remaining budget covers it. Training selects `b0` from 12 values by maximum observed training clicks, with lower spend breaking ties. The test budget is half its total logged market-price sum and is shared by all policies. The separate request-order controller adjusts bids by cumulative spend error; it is a volume proxy, not intraday pacing.

Derived metrics include observed CTR, budget utilization, win rate and cost per click. Null CPC means no clicks. A 10,000-request bucket query helps separate shifts in available volume, market prices, upstream predictions and observed click rates. Preserve the source's integer price units rather than labeling them as USD.

## Consulting and enablement use

1. Establish the advertiser objective and cost constraint before selecting a bidding policy.
2. Walk through the data dictionary, spend cap, training sweep and holdout comparison with a trader.
3. Investigate price, predicted response and observed response before recommending a change.
4. Record feature feedback using `feedback_template.csv`; prioritize reproducible evidence and a clear product question.
5. For a beta rollout, define success and rollback thresholds before launch, retain a baseline and review customer metrics.

## Sources and scope

Primary: [authors' experiment repository](https://github.com/wnzhang/rtbcontrol), supporting *Feedback Control of Real-Time Display Advertising*. Its README identifies the demo as sampled iPinYou advertiser 1458 data, and `python/make-yzpc.py` documents the four-field transformation.

Backup for broader first-price experiments: [BAT auto-bidding benchmark](https://github.com/avito-tech/bat-autobidding-benchmark) and its [public dataset](https://zenodo.org/records/14794182). BAT uses a dedicated schema adapter and simulator.
