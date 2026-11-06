# Brand and Consumer Readiness

Codex-created extension connecting the repository's executed, 64,000-record historical randomized campaign analysis with brand approvals, content governance, community activation deliverables, and operational launch readiness.

Run with Python's standard library from this directory:

```sh
python pipeline.py
python -m unittest -v
```

The upstream `campaign_experiments` module supplies assignment-arm totals. Its primary publisher dataset is [Kevin Hillstrom's MineThatData challenge](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html), with [Criteo Uplift v2](https://ailab.criteo.com/criteo-uplift-prediction-dataset/) as an unexecuted backup requiring a separate adapter. The extension does not change upstream data or estimators.

The review requires eight approvals: brand, content, capacity, referral journey, tracking, partner deliverables, family experience, and budget. An approval missing from the input remains open; empty capacity never becomes zero or approval. Expected responses exceeding available slots hold the campaign. Demonstration rows exercise both ready and held states.

`templates/content_inventory.csv` tracks provider bios, blogs, and sports activations. `templates/mystery_shop.csv` records an observed journey, issue owner, follow-up date, and resolution. No mystery shopping or provider-content review is claimed to have occurred. Blank templates are intended for authorized operational data.

Budget sensitivity uses incremental conversion = treatment conversions / treatment assignments − control conversions / control assignments. Illustrative contribution = incremental conversion × audience × assumed revenue per conversion × contribution margin − audience × contact cost. Contact cost, margin, future audience, and value are explicit assumptions; these calculations do not establish patient acquisition, clinical demand, retention, sponsorship ROI, or realized revenue.

Results include a program readiness CSV, three economic sensitivity cases, validation metadata, and boundary-test output. Every assignment remains in the source denominator. Source provenance and statistical uncertainty remain documented in the upstream module.
