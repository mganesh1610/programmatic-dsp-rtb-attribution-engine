# Programmatic DSP Bid Shading & Omnichannel Attribution Engine

## Reproducible public-data module

[Campaign Experiment Analytics](campaign_experiments/README.md) adds a 64,000-customer randomized email evaluation with intent-to-treat SQL, conversion intervals, Holm adjustment, and ROI modeling.

[Public auction replay and diagnostics](public_replay/README.md) provides a pinned 200,000-record iPinYou sample, schema validation, SQLite/SQL diagnostics, training-only parameter selection and holdout evaluation. In the executed 100,000-record test replay, the selected linear policy retained 45 clicks versus a constant-bid baseline while lowering replay cost per click by 31.6%. See the complete [machine-readable results](public_replay/results/validation_summary.json).

End-to-end programmatic advertising technology, RTB bid optimization, multi-touch attribution, DMP/CDP audience segmentation, and trading-desk analytics suite built with **Python, SQL (`SQL Joins & CTEs`), BigQuery, Power BI, Looker Studio, and Tableau**.

---

## 1. Architecture & Technical Capabilities

1. **First-Price RTB Auction Bid Shading & ML Pacing Optimization (`src/dsp_rtb_attribution_pipeline.py`)**
   - Models impression valuation $v_i = \text{pCTR}_i \times \text{pCVR}_i \times V_{\text{conv}} \times 1000$ across **250,000+ programmatic RTB auctions** (`Open Exchange`, `Private Marketplace (PMP)`, and `Programmatic Guaranteed (PG)` deals) spanning **E-Commerce & Retail, Automotive, Entertainment & Streaming, and Consumer Tech** verticals.
   - Calibrates nonlinear first-price bid shading factors $\lambda_i^* \in [0.61, 0.85]$ against log-normal clearing price distributions to maximize expected surplus $(v_i - b_i)\Pr(\text{win} \mid b_i, f_i)$, reducing average winning CPM by **30.39%** and cutting effective CPA by **22%+ to 33.68%** while reallocating budget into high-propensity inventory.

2. **Shapley Value & First-Order Markov Chain Multi-Touch Attribution (`outputs/shapley_markov_attribution_channel_metrics.csv`)**
   - Computes exact cooperative game-theoretic **Shapley Values**:
     $$\phi_j(v) = \sum_{S \subseteq N \setminus \{j\}} \frac{|S|!(|N|-|S|-1)!}{|N|!} \left[v(S \cup \{j\}) - v(S)\right]$$
     alongside **First-Order Markov Chain Removal Effects** across **Programmatic Display, In-Stream Video, OTT/CTV, Paid Search (SEM), and Organic Search (SEO)** (`$2.1M+` annual media plan driving `24,600+` annual / `20,000+` peak monthly conversions).
   - Quantifies upper-funnel OTT/CTV (`+9.35%` credit shift vs. Last-Touch) and In-Stream Video (`+4.40%` credit shift) assist value for annual brand and media planning.

3. **DMP / CDP First-Party Audience Segmentation, Intraday Pacing & Ad Verification QA (`outputs/dmp_cdp_audience_segment_lift.csv`, `outputs/trader_onboarding_beta_qa_scorecard.csv`)**
   - Evaluates **60+ concurrent omnichannel campaigns** across 1st-party CDP/GA4/GTM segments, DMP in-market cohorts, and contextual key-value PMP/PG deals, reducing pacing under-delivery by **30–45% (`37.58%` mean)** and lifting average CPM efficiency by **8–12% (`9.88%` mean)**.
   - Integrates **IAS, DoubleVerify, and MOAT** verification metrics (Viewability, Invalid Traffic `IVT`, Video Completion Rate `VCR`, and `VAST 4.x` error diagnostics) and tracks programmatic trader onboarding and beta feature enablement (`50%` faster onboarding turnaround across `10+` traders).

4. **Omnichannel Marketplace Spend-to-Sales & Retained Order CAC Reconciliation (`marketplace_spend_to_sales/marketplace_channel_economics_reconciliation.csv`)**
   - Reconciles omnichannel media spend, retained orders, contribution margin, and randomized outreach incrementality lift (`+5.05 pts`) across **289,239 stored marketplace records and 68 tables**, uncovering **$518.72 CAC savings per attributed order** between Display (`$1,115.87` CAC) and Paid Search (`$1,634.59` CAC).

---

## 2. Verified Validation Results

### A. RTB Bid Shading Performance by Vertical (`outputs/rtb_bid_shading_summary.csv`)

| Vertical | Auctions Evaluated | Shaded Win Rate (%) | Avg Floor CPM ($) | Avg Unshaded Win CPM ($) | Avg Shaded Win CPM ($) | Avg Shading Factor ($\lambda^*$) | CPA Reduction (%) | Shaded ROAS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E-Commerce & Retail** | 95,041 | 71.11% | $4.76 | $6.98 | $4.86 | 0.697 | **33.36%** | **3.02x** |
| **Automotive** | 64,956 | 71.63% | $4.76 | $12.16 | $8.44 | 0.692 | **33.62%** | **3.06x** |
| **Entertainment & Streaming** | 50,064 | 71.16% | $4.77 | $5.22 | $3.65 | 0.698 | **33.15%** | **2.84x** |
| **Consumer Tech** | 39,939 | 71.36% | $4.76 | $7.70 | $5.34 | 0.694 | **33.65%** | **3.05x** |

### B. Multi-Touch Attribution Channel Allocation (`outputs/shapley_markov_attribution_channel_metrics.csv`)

| Channel | Annual Spend ($) | Last-Touch Share (%) | Shapley Share (%) | Markov Removal Share (%) | Blended MTA Share (%) | Attributed Conversions | Upper-Funnel Credit Delta (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Programmatic Display** | $420,000 | 14.20% | 17.52% | 17.60% | **17.56%** | 4,320 | +3.36% |
| **In-Stream Video** | $510,000 | 15.80% | 20.00% | 20.40% | **20.20%** | 4,969 | +4.40% |
| **OTT / CTV** | $640,000 | 13.50% | 22.60% | 23.10% | **22.85%** | 5,621 | +9.35% |
| **Paid Search (SEM)** | $390,000 | 36.40% | 25.49% | 23.80% | **24.64%** | 6,063 | -11.76% |
| **Organic Search (SEO)** | $140,000 | 20.10% | 14.39% | 15.10% | **14.74%** | 3,627 | -5.36% |

### C. Marketplace Spend-to-Sales CAC Reconciliation (`marketplace_spend_to_sales/marketplace_channel_economics_reconciliation.csv`)

| Channel | Monthly Spend ($) | Retained Orders | Attributed CAC ($) | CAC Savings vs. Paid Search ($) |
| :--- | :---: | :---: | :---: | :---: |
| **Display** | $24,549.03 | 22 | **$1,115.87** | **$518.72** |
| **Affiliate** | $25,793.18 | 20 | $1,289.66 | $344.93 |
| **Paid Social** | $26,187.44 | 19 | $1,378.29 | $256.30 |
| **Email** | $24,313.04 | 17 | $1,430.18 | $204.41 |
| **Paid Search** | $26,153.47 | 16 | $1,634.59 | $0.00 |

---

## 3. Repository Structure

```text
programmatic-dsp-rtb-attribution-engine/
├── README.md
├── src/
│   └── dsp_rtb_attribution_pipeline.py
├── sql/
│   └── programmatic_attribution_and_pacing_queries.sql
├── marketplace_spend_to_sales/
│   └── marketplace_channel_economics_reconciliation.csv
├── notebooks/
│   └── programmatic_dsp_bid_shading_and_attribution_walkthrough.ipynb
├── docs/
│   └── DATA_DICTIONARY_AND_SCHEMA.md
└── outputs/
    ├── rtb_bid_shading_summary.csv
    ├── shapley_markov_attribution_channel_metrics.csv
    ├── dmp_cdp_audience_segment_lift.csv
    ├── trader_onboarding_beta_qa_scorecard.csv
    └── validation_summary.json
```

## 4. Quick Start

```bash
python3 src/dsp_rtb_attribution_pipeline.py
```
