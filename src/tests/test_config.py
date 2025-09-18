#!/usr/bin/python3
import unittest, sys
sys.path.append('..')
sys.path.append('../core')

from framework.lib.config import Config

class TestCase(unittest.TestCase):    
    def setUp(self):
        self.config = Config('config.json')
        
    def test_get_owner(self):                
        assert self.config.owner == "OWNER"
        
    def test_get_password(self):
        assert self.config.password == "123456"
        
    def test_default_channels(self):
        print (self.config.default_channels)
        
    def test_get_plugin_ranch_default_channels(self):
        print (self.config.plugins['ranch']['channels'])
        assert self.config.plugins['ranch']['channels'][0] == "CHANNEL" 
        
        

if __name__ == "__main__":
    unittest.main() # run all tests