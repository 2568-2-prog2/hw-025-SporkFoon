import unittest

class ProgrammingTest(unittest.TestCase):
    def test_case1(self):
        a = 50.00000000001
        b = a + 0.00000000002
        print(a,b)
        self.assertAlmostEqual(a,b,places=5)
        
    def test_case2(self):
        a = 50.000000000000000000001
        b = a - 0.000000000000000000002
        self.assertEqual(a,b)
    
    def test_case3(self):
        
        s = '11 22 33 44 55'
        q = s.split(4,"-")
        
        with self.assertRaises(TypeError):
            q = s.split(4,"-")
            print(q)

if __name__ == '__main__':
    unittest.main()