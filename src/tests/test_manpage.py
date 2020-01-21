#!/usr/bin/python3
import unittest, sys
sys.path.append('..')
sys.path.append('../core')

from   core.Manpage import Manpage

class TestCase(unittest.TestCase):    
    def setUp(self):
        self.man = Manpage()
        
    def test_manual(self):
        self.man.add_command("!test", "its doing nothing")        
        assert self.man.get_manpage() == "!test : its doing nothing\n"
        
    def test_manual_2(self):
        self.man.add_command("!test", "its doing nothing")
        self.man.add_command("!test_2", "its doing nothing")        
        assert self.man.get_manpage() == "!test : its doing nothing\n!test_2 : its doing nothing\n"
    

if __name__ == "__main__":
    unittest.main() # run all tests

