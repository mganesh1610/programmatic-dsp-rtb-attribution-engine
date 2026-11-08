# Campaign Experiment Analytics

An evaluation of the Hillstrom randomized email experiment adding intent-to-treat campaign measurement, SQL reconciliation, conversion intervals, and ROI modeling.

## Run

From this directory, use Python 3.12 in a virtual environment:

```sh
python -m pip install -r requirements.txt
python pipeline.py
python -m unittest -v
```

The pinned source is downloaded on the first run. The publisher's HTTP endpoint is used because its HTTPS certificate chain was unavailable during verification. SHA-256 is required before parsing. Source rows and SQLite are not committed; aggregate CSV, JSON, HTML review, and test output are included in `results/`.

## Design and measured results

All **64,000 assigned customers** remain in the denominator over the original two-week outcome window. Men’s email has 21,307 assignments and 267 conversions; women’s email has 21,387 and 189; control has 21,306 and 122. Do not subset to visitors, openers, or converters before comparing assignment arms.

Men’s email versus control has a **0.6805 percentage-point** absolute conversion difference, individual Wilson-Newcombe 95% interval **0.5014–0.8641 points**, and Holm-adjusted two-sided p-value **3.0464e-13**. Women’s email versus control has a **0.3111-point** difference, interval **0.1502–0.4745 points**, and adjusted p-value **0.0001571**. Both planned comparisons are shown.

All **10 source/SQL reconciliation checks** and **7 boundary tests** passed in the November 6, 2026 run. Assignment-ratio chi-square and pre-treatment standardized mean differences are included in `results/validation.json`. The two conversion p-values use Holm adjustment; displayed intervals are individual Wilson-Newcombe 95% intervals.

## Architecture and formulations

Pinned publisher CSV → schema checks → row-preserving SQLite load → SQL arm counts and outcome sums → Python rate and spend contrasts → multiplicity adjustment, sensitivity assumptions, and business review.

Conversion difference = converted_treatment / assigned_treatment − converted_control / assigned_control. Its interval combines two Wilson score intervals using the Newcombe method. The null test uses the pooled two-proportion standard error. Spend difference is mean spend per assigned treatment customer minus mean spend per assigned control customer, with a Welch t interval.

Incremental contribution = mean spend difference × contribution margin − contact cost. The default .30 margin and .01 contact cost are configurable financial parameters. Incremental ROI divides that contribution by contact cost.

## Data and schema

Primary: Kevin Hillstrom’s [MineThatData E-Mail Analytics and Data Mining Challenge](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html), 2008. The [TensorFlow Datasets catalog](https://www.tensorflow.org/datasets/catalog/hillstrom) independently documents the randomized three-arm design and 64,000 rows. Download: `http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv`. SHA-256: `0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece`.

The 12 source fields are `recency`, `history_segment`, `history`, `mens`, `womens`, `zip_code`, `newbie`, `channel`, `segment`, `visit`, `conversion`, and `spend`. Pre-assignment features precede segment; assignment is `segment`; outcomes are visit, conversion, spend. A one-based `source_row` preserves every record without inventing a business customer key. Duplicate-looking rows are not automatically removed. Currency code is not supplied, so spend remains in source units. Public availability does not imply a new license grant; source data are not redistributed here.

Backup: [Criteo Uplift v2](https://ailab.criteo.com/criteo-uplift-prediction-dataset/), 13,979,592 records under CC BY-NC-SA 4.0 terms. Its binary treatment, visits, conversions, and anonymized features use a dedicated two-arm assignment-ratio adapter.

## Review artifacts

`analysis.sql` owns the denominators. `results/assigned_arm_metrics.csv` supplies SQL aggregates; `contrast_results.csv` supplies estimates and intervals; `validation.json` records source hash, balance, tests, assumptions, and interpretation. `review.html` presents both contrasts. The seven unit tests cover invalid and empty groups, zero-event uncertainty, equal rates, Holm ordering/capping, and spend arithmetic.
