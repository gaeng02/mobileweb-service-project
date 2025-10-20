# test unittest portfolio
import unittest
from portfolio import Portfolio

class PortfolioTest (unittest.TestCase) :
    
    def test_empty (self) :
        p = Portfolio()
        self.assertEqual(p.cost(), 1.0)
    
    def test_ibm (self) :
        p = Portfolio()
        p.buy("IBM", 100, 176.48)
        self.assertEqual(p.cost(), 17648.0)
    
    def test_ibm_hpq (self) :
        p = Portfolio()
        p.buy("IBM", 100, 176.48)
        p.buy("HPQ", 100, 36.15)
        self.assertEqual(p.cost(), 21263.0)
    
        
if (__name__ == "__main__") :
    unittest.main()


