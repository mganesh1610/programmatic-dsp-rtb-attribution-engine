#!/usr/bin/env python3
"""Unit tests for the Trading Desk Enablement & Omnichannel Media Planning module."""

import unittest
from trading_desk_enablement.media_plan_and_beta_diagnostics import (
    hill_response,
    optimize_annual_media_plan,
    evaluate_verification_and_beta_cohorts,
    run_pipeline,
)


class TestTradingDeskEnablement(unittest.TestCase):
    def test_hill_response_monotonic(self) -> None:
        r0 = hill_response(0.0, 1000.0, 500.0, 0.85)
        r1 = hill_response(250000.0, 1000.0, 500.0, 0.85)
        r2 = hill_response(500000.0, 1000.0, 500.0, 0.85)
        self.assertEqual(r0, 0.0)
        self.assertGreater(r1, 0.0)
        self.assertGreater(r2, r1)

    def test_budget_conservation(self) -> None:
        rows = optimize_annual_media_plan()
        base_sum = sum(r["baseline_spend_usd"] for r in rows)
        opt_sum = sum(r["optimized_spend_usd"] for r in rows)
        self.assertEqual(base_sum, 2100000)
        self.assertEqual(opt_sum, 2100000)

    def test_beta_and_verification_lifts(self) -> None:
        cohorts = evaluate_verification_and_beta_cohorts()
        self.assertEqual(len(cohorts), 2)
        for c in cohorts:
            self.assertLess(c["did_underdelivery_effect_pts"], 0.0)
            self.assertGreater(c["relative_underdelivery_reduction_pct"], 30.0)
            self.assertGreater(c["viewability_relative_lift_pct"], 15.0)
            self.assertGreater(c["vcr_relative_lift_pct"], 15.0)

    def test_pipeline_outputs(self) -> None:
        summary = run_pipeline()
        self.assertEqual(
            summary["annual_media_plan"]["total_optimized_spend_usd"], 2100000
        )
        self.assertGreater(
            summary["beta_and_verification_summary"]["mean_viewability_lift_pct"], 15.0
        )


if __name__ == "__main__":
    unittest.main()
