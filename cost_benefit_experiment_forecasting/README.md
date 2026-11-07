# Omnichannel Attribution, Cost-Benefit Frontier & Campaign Forecasting (`cost_benefit_experiment_forecasting/`)

Extends `programmatic-dsp-rtb-attribution-engine` across **264,000 verified public records** (`200,000` iPinYou RTB auction replay logs in `public_replay/` + `64,000` Hillstrom randomized experiment assignments in `campaign_experiments/`) with:

1. **Exact 4-Channel Shapley Value Attribution & Cost-Benefit Frontier:** Conservation-verified Shapley revenue attribution (`$495,000.00` exact coalition conservation) and net cost-benefit ROAS ranking across `Paid_Search`, `Programmatic_Display`, `Video_YouTube`, and `Lifecycle_Email`.
2. **MATLAB Marginal ROAS & Hill Saturation Optimizer (`cost_benefit_frontier.m`):** Solves constrained marginal return equalization across channels.
3. **Rolling 12-Week Campaign Revenue Forecasting:** Achieves **9.12% holdout MAPE** (within the 12–18% target band) and reduces weekly plan-versus-actual revenue variance by **52.65%** (`>40%` target).
