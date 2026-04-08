import unittest

class ProgrammingTest(unittest.TestCase):
    def test_case1(self):
        a = 50.00000000001
        b = a + 0.00000000002
        print(a,b)
        self.assertAlmostEqual(a,b,places=50)
        
    def test_case2(self):
        a = 50.000000000000000000001
        b = a - 0.000000000000000000002
        self.assertEqual(a,b)
        
