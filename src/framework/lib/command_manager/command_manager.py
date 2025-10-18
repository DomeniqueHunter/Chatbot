from framework.lib.reaction import Reaction

class CommandManager(Reaction):
    
    def __init__(self, manpage=None, defaultExceptionFunction=None) -> None:
        super().__init__(defaultExceptionFunction)
        self.manpage = manpage
    
    def add_action(self, handler, function, man_text="", role=None, section=None, no_help=False) -> None:
        if not no_help:
            handler = self.manpage.add_command(handler, man_text, role, section)
            
        print(function.__name__)
        super().add_action(handler, function)