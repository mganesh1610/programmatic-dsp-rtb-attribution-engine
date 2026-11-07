#!/usr/bin/env python3
"""Unit tests for Omnichannel Attribution, Cost-Benefit & Campaign Forecasting Module."""

from __future__ import annotations

import unittest
from cost_benefit_forecasting_engine import compute_shapley_and_cost_benefit


class TestCostBenefitForecasting(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = compute_shapley_and_cost_benefit()

    def test_01_combined_record_scale(self) -> None:
        scale = self.summary["combined_upstream_records"]
        self.assertEqual(scale["ipinyou_auction_replay_rows"], 200000)
        self.assertEqual(scale["hillstrom_randomized_experiment_rows"], 64000)
        self.assertEqual(scale["total_verified_records"], 264000)

    def test_02_shapley_revenue_conservation(self) -> None:
        chk = self.summary["shapley_conservation_check"]
        self.assertEqual(chk["channel_count"], 4)
        self.assertAlmostEqual(
            chk["total_attributed_revenue_usd"],
            chk["grand_coalition_revenue_usd"],
            places=2,
        )

    def test_03_forecasting_mape_and_variance_reduction(self) -> None:
        fc = self.summary["rolling_12_week_forecasting"]
        self.assertLessEqual(fc["model_forecast_mape_pct"], 12.0)
        self.assertGreaterEqual(fc["plan_vs_actual_variance_reduction_pct"], 40.0)


if __name__ == "__main__":
    unittest.main()
