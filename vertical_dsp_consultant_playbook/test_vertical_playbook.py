import unittest
from vertical_attribution_and_shading import compute_weighted_cpa_reduction

class TestVerticalPlaybook(unittest.TestCase):
    def test_vertical_aggregation(self):
        summary = compute_weighted_cpa_reduction()
        self.assertEqual(summary["total_auction_logs"], 250000)
        self.assertAlmostEqual(summary["weighted_effective_cpa_reduction_pct"], 31.6, places=1)
        self.assertEqual(len(summary["verticals"]), 4)

if __name__ == "__main__":
    unittest.main()
