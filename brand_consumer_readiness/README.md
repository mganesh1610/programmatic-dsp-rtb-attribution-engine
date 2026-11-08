# Brand and Consumer Readiness

Extension connecting the repository's 64,000-record randomized campaign analysis with brand approvals, content governance, community activation deliverables, and operational launch readiness.

Run with Python's standard library from this directory:

```sh
python pipeline.py
python -m unittest -v
```

The upstream `campaign_experiments` module supplies assignment-arm totals. Its primary publisher dataset is [Kevin Hillstrom's MineThatData challenge](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html), with [Criteo Uplift v2](https://ailab.criteo.com/criteo-uplift-prediction-dataset/) documented as a secondary schema.

The review requires eight approvals: brand, content, capacity, referral journey, tracking, partner deliverables, family experience, and budget. An approval missing from the input remains open; empty capacity never becomes zero or approval. Expected responses exceeding available slots hold the campaign.

`templates/content_inventory.csv` tracks provider bios, blogs, and sports activations. `templates/mystery_shop.csv` records an observed journey, issue owner, follow-up date, and resolution.

Budget sensitivity uses incremental conversion = treatment conversions / treatment assignments − control conversions / control assignments. Contribution = incremental conversion × audience × revenue per conversion × contribution margin − audience × contact cost.

Results include a program readiness CSV, three economic sensitivity cases, validation metadata, and boundary-test output. Every assignment remains in the source denominator.
