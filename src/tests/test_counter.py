#!/usr/bin/python3
import unittest, sys
sys.path.append('..')
sys.path.append('../core')

from core.Counter import Counter

class TestCase(unittest.TestCase):    
    def setUp(self):
        self.counter = Counter (10)
        
    def test_up_tp_1(self):                
        assert self.counter.tick() == False
        
    def test_up_to_10(self):
        for i in range(9):
            assert self.counter.tick() == False
        
        assert self.counter.tick() == True        

if __name__ == "__main__":
    unittest.main() # run all tests