#!/usr/bin/python3.10

import unittest, sys
sys.path.append('..')
sys.path.append('../core')

from core.lib.Manpage.Manpage import Manpage
from core.lib.Manpage.BotMock import BotMock


class TestCase(unittest.TestCase):    
    def setUp(self):
        self.manpage = Manpage(BotMock())
    
    def test_step1_add_section(self):
        self.manpage.add_section("Test")        
        assert ["Debug (Owner)", "Test"] == self.manpage.sections
        
    def test_step2_add_command_owner(self):
        self.manpage.add_command("!test <a>", "test a", role="owner", section="Bot (Admin)")
        
        assert ["Debug (Owner)", "Bot (Admin)"] == self.manpage.sections
        assert "Bot (Admin)!test <a> : test a" == self.manpage.show('Owner').replace('\n', '')
        assert "" == self.manpage.show('Admin').replace('\n', '')
        assert "" == self.manpage.show('User').replace('\n', '')
        
    def test_step3_add_command_admin(self):
        self.manpage.add_command("!test <a>", "test a", role="admin", section="Bot (Admin)")
        
        assert ["Debug (Owner)", "Bot (Admin)"] == self.manpage.sections
        assert "Bot (Admin)!test <a> : test a" == self.manpage.show('Owner').replace('\n', '')
        assert "Bot (Admin)!test <a> : test a" == self.manpage.show('Admin').replace('\n', '')
        assert "" == self.manpage.show('User').replace('\n', '')
        
    def test_step4_add_command_user(self):
        self.manpage.add_command("!test <a>", "test a", role="user", section="Bot (Admin)")
        
        assert ["Debug (Owner)", "Bot (Admin)"] == self.manpage.sections
        assert "Bot (Admin)!test <a> : test a" == self.manpage.show('Owner').replace('\n', '')
        assert "Bot (Admin)!test <a> : test a" == self.manpage.show('Admin').replace('\n', '')
        assert "Bot (Admin)!test <a> : test a" == self.manpage.show('User').replace('\n', '')
        
        
    def test_step5_old_style(self):
        self.manpage.add_command("!debug", "Text1")    
        
        assert ["Debug (Owner)"] == self.manpage.sections
        assert "Debug (Owner)!debug : Text1" == self.manpage.show('Owner').replace('\n', '')   

if __name__ == "__main__":
    unittest.main() # run all tests

