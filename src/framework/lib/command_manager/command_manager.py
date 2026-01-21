from framework.lib.reaction import Reaction
from collections import defaultdict


class CommandManager(Reaction):
    
    def __init__(self, manpage=None, defaultExceptionFunction=None) -> None:
        super().__init__(defaultExceptionFunction)
        self.manpage = manpage
        self.statistics = defaultdict(int)
    
    def add_action(self, handler, function, man_text="", role=None, section=None, no_help=False) -> None:
        if not no_help:
            handler = self.manpage.add_command(handler, man_text, role, section)
            
        super().add_action(handler, function)
        
    def react(self, handler, *args):
        if handler in self.actions: 
            self.statistics[handler] += 1
        
        return super().react(handler, *args)
    
    def show_statistics(self) -> dict:
        return dict(self.statistics)
    
