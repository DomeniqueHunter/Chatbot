from framework.lib.reaction import Reaction, EXCEPTION_REACTION_HANDLER
from collections import defaultdict


class CommandManager(Reaction):
    
    def __init__(self, manpage=None, *,defaultExceptionFunction=None, prefix:str="!") -> None:
        super().__init__(defaultExceptionFunction)
        self.manpage = manpage
        self.statistics = defaultdict(int)
        self.prefix = prefix
    
    def add_action(self, handler, function, man_text="", role=None, section=None, no_help=False) -> None:
        if not (handler.startswith(self.prefix) or handler == EXCEPTION_REACTION_HANDLER): 
            print(f"{handler} is not valid!")
            return None 
        
        if not no_help:
            handler = self.manpage.add_command(handler, man_text, role, section)
            
        super().add_action(handler, function)
        
    def react(self, handler, *args):
        if handler in self.actions: 
            self.statistics[handler] += 1
        
        return super().react(handler, *args)
    
    def show_statistics(self) -> dict:
        return dict(self.statistics)
