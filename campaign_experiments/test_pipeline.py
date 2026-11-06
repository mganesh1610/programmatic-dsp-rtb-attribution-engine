import unittest
from pipeline import difference_of_rates,holm_adjust,welch_mean_difference


class ExperimentTests(unittest.TestCase):
    def test_identical_rates(self):
        out=difference_of_rates(10,100,10,100)
        self.assertEqual(out["absolute_conversion_difference"],0)
        self.assertEqual(out["two_sided_p_value"],1)

    def test_all_zeros(self):
        out=difference_of_rates(0,20,0,20)
        self.assertEqual(out["two_sided_p_value"],1)
        self.assertLess(out["approximate_95_ci"][0],0)
        self.assertGreater(out["approximate_95_ci"][1],0)

    def test_empty_group_rejected(self):
        with self.assertRaises(ValueError):
            difference_of_rates(0,0,1,5)

    def test_invalid_success_count(self):
        with self.assertRaises(ValueError):
            difference_of_rates(11,10,1,5)

    def test_holm_monotonic(self):
        self.assertEqual(holm_adjust([.04,.01,.03]),[.06,.03,.06])

    def test_holm_capped(self):
        self.assertEqual(holm_adjust([.9,.8]),[1.,1.])

    def test_spend_difference(self):
        out=welch_mean_difference([1,2,3],[0,1,2])
        self.assertEqual(out["mean_difference"],1)
        self.assertLess(out["approximate_95_ci"][0],1)
        self.assertGreater(out["approximate_95_ci"][1],1)


if __name__=="__main__":
    unittest.main()
