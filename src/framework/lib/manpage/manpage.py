
class Manpage():
    
    def __init__(self, bot=None, default_section:str="Debug (Owner)", default_role:str="owner") -> None:
        self.commands  = {}
        self.bot = bot
        self.sections = []
        self.roles = ['user', 'admin', 'owner']
        
        self.add_section(default_section)
        
        self._default_section = default_section
        self._default_role = default_role
        
        self._counter = 0
    
    def add_bot(self, bot) -> None:
        self.bot = bot
        
    def add_section(self, section:str) -> None:
        if section not in self.sections:
            self.sections.append(section)
            
            self.commands[section] = {}
            for role in self.roles:
                self.commands[section][role] = []

    def _add_help(self, command:str, man_text:str=None, role:str=None, section:str=None) -> str:
        if man_text and section and role and man_text:
            if section not in self.sections:
                self.add_section(section)
                
            self.commands[section][role].append(f"{command} : {man_text}\n")
            return command.split(maxsplit=1)[0]
            
    def add_command(self, command:str="", man_text:str="", role:str="", section:str="") -> str:
        if not role:
            role = self._default_role
        if not section:
            section = self._default_section
        print(f"Commands - Add Command: {command} {section} {role}")
        return self._add_help(command, man_text, role, section)
                
    def get_manpage(self, all:bool=False) -> str:
        return_string = ''
        
        for cmd_string in self.commands:
            #print(cmd_string)
            return_string += cmd_string
        if all:
            for cmd_string in self.commands:
                return_string += cmd_string
        #print (return_string)
        return return_string
    
    def show(self, user:str) -> str:
        man_text = ""
        
        for section in self.sections:
            show_headline = True
            for role in self.roles:
                if self.bot.has_role(role, user):
                    for text in self.commands[section][role]:
                        if show_headline:
                            man_text += f"\n{section}\n"
                            show_headline = False
                            
                        man_text += text
        
        self._counter += 1
        return man_text
    
    def counter(self) -> int:
        return self._counter
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
            