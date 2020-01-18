
class Manpage():
    
    def __init__(self):
        self.commands  = []
        
    def add_command (self, command = None, text = ""):
        if command:
            entry = "{} : {}\n".format(command, text)
            self.commands.append(entry)
        else:
            print ("no command given!")
            
    def get_manpage(self, all = False):
        return_string = ''
        
        print ("LEN: {}".format(len(self.commands)))
        
        for cmd_string in self.commands:
            print(cmd_string)
            return_string += cmd_string
        if all:
            for cmd_string in self.commands:
                return_string += cmd_string
        #print (return_string)
        return return_string
            