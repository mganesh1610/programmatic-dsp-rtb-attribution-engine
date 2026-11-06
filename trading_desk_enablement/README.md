# Trading Desk Enablement, Omnichannel Media Planning & Beta Feature Diagnostics

This module complements `public_replay/` and `src/dsp_rtb_attribution_pipeline.py` with a zero-dependency Python simulation and validation suite for:

1. **Annual Brand & Omnichannel Media Planning (`optimize_annual_media_plan`)**:
   - Models diminishing-returns **Hill Saturation Response Curves** $R_c(S_c) = \alpha_c \frac{S_c^{\gamma_c}}{\kappa_c^{\gamma_c} + S_c^{\gamma_c}}$ weighted by Shapley Value and First-Order Markov Chain attribution shares across **E-Commerce & Retail, Automotive, and Entertainment & Streaming** verticals (`$2.1M` annual budget across DSP Display, In-Stream Video, OTT/CTV, Paid Search SEM, and Organic Search SEO).
2. **Trader Onboarding, Beta Rollouts & Ad Verification Diagnostics (`evaluate_verification_and_beta_cohorts`)**:
   - Computes **Difference-in-Differences (DiD)** treatment effects for S2S header-bidding / bid-shading beta rollouts and 1st-party CDP/GA4 + DMP audience segment activations across **10+ programmatic traders**, **50+ demand partners**, and **60+ campaigns**.
   - Tracks **IAS, DoubleVerify, and MOAT** viewability (`+16.5%` to `+18.1%` relative lift), video completion rate (`+15.8%` to `+15.9%` relative lift), and invalid traffic (`IVT < 1.5%`) controls.

## Run

```bash
python3 trading_desk_enablement/media_plan_and_beta_diagnostics.py
python3 -m unittest discover -s trading_desk_enablement -p 'test_*.py' -v
```
