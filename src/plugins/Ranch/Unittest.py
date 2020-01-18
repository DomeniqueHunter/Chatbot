#!/usr/bin/env python3

import unittest
from Ranch import Ranch
from Cow import Cow
from Worker import Worker

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.ranch = Ranch("H-Milk")
        self.ranch.add_cow("Troya Williams", 100)
        self.cow = Cow("Taylor", 200)
        self.worker = Worker("Domenique")
    
    def test_new_ranch(self):
        self.assertEqual(self.ranch.name, "H-Milk", "H-Milk ist der name")
        
    def test_add_cow(self):
        self.assertEqual(self.ranch.cows["Troya Williams"].name, "Troya Williams", "Cow Name: Troya Williams")
    
    def test_milk_the_cow(self):
        c = self.ranch.cows["Troya Williams"]
        a = c.milk()
        self.assertGreaterEqual(a, 20, "bigger or equal than 20")
    
    def test_milk_cow_twice(self):
        a = self.ranch.worker_milks_cow(self.worker, self.cow)
        self.assertGreaterEqual(a, 20, "bigger or equal than 20")
        b = self.ranch.worker_milks_cow(self.worker, self.cow)
        self.assertEqual(b, None, "can't milk cow")
        
    
if __name__ == '__main__':
    unittest.main()