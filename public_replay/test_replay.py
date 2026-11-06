import tempfile
import unittest
from pathlib import Path
from auction_diagnostics import load_rows, replay, select_bid


class ReplayTests(unittest.TestCase):
    def test_budget_never_exceeded(self):
        result = replay([(1, 7, .5, "1")] * 3, 100, .5, 10)
        self.assertEqual((result["spend_units"], result["wins"], result["clicks"]), (7, 1, 1))

    def test_strict_tie_and_zero_bid(self):
        self.assertEqual(replay([(1, 10, .5, "1")], 10, .5, 100)["wins"], 0)
        self.assertEqual(replay([(1, 0, 0, "1")], 10, .5, 0)["wins"], 0)

    def test_no_clicks_has_no_cpc(self):
        self.assertIsNone(replay([(0, 1, .5, "1")], 20, .5, 10)["cost_per_click_units"])

    def test_schema_rejects_invalid_probability(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_text("0\t1\tNaN\t1\n")
            with self.assertRaises(ValueError):
                load_rows(path)

    def test_selection_uses_training_only(self):
        train = [(1, 15, .5, "1"), (0, 1, .01, "1")]
        selected, trials = select_bid(train, .5, 20)
        self.assertEqual(selected, 20)
        self.assertEqual(len(trials), 12)


if __name__ == "__main__":
    unittest.main()
