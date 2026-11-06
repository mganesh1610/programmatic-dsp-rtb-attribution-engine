import unittest
from pipeline import GATES,launch_status,contribution_scenarios

class ReadinessTests(unittest.TestCase):
    def ready(self):return dict({g:'yes' for g in GATES},available_slots='10',expected_responses='5')
    def test_ready(self):self.assertEqual(launch_status(self.ready()),('READY',[]))
    def test_capacity_shortfall(self):
        row=self.ready();row['expected_responses']='11';self.assertIn('capacity_shortfall',launch_status(row)[1])
    def test_missing_approval(self):
        row=self.ready();del row['brand_approved'];self.assertEqual(launch_status(row)[0],'HOLD')
    def test_empty_capacity(self):
        row=self.ready();row['available_slots']='';self.assertEqual(launch_status(row)[0],'HOLD')
    def test_negative_capacity(self):
        row=self.ready();row['available_slots']='-1';self.assertEqual(launch_status(row)[0],'HOLD')
    def test_zero_spend(self):self.assertIsNone(contribution_scenarios(.01,100,.3,0,25)['roi'])
    def test_contribution(self):self.assertAlmostEqual(contribution_scenarios(.01,100,.3,.01,25)['incremental_contribution'],6.5)

if __name__=='__main__':unittest.main()
