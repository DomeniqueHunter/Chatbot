import inspect
from .reaction import EXCEPTION_REACTION_HANDLER


class Multi_Reaction(): 

    def __init__(self, defaultExceptionFunction=None):
        self.actions = {}
        self.index = 0
        if defaultExceptionFunction and (inspect.isfunction(defaultExceptionFunction) or inspect.ismethod(defaultExceptionFunction)):
            self.add_action(EXCEPTION_REACTION_HANDLER, defaultExceptionFunction)
        else:
            self.add_action(EXCEPTION_REACTION_HANDLER, self.__defaultException)
        
    def add_action(self, handler, function):
        if handler not in self.actions:
            self.actions[handler] = {}    
        
        if inspect.isfunction(function):
            self.actions[handler][self.index] = {}   
            self.actions[handler][self.index]['function'] = function
            self.actions[handler][self.index]['args'] = function.__code__.co_argcount
            print(f"+ set multi action for function: {str(self.index)}.) {handler} ({str(self.actions[handler][self.index]['args'])})")
            
        elif inspect.ismethod(function): 
            self.actions[handler][self.index] = {}   
            self.actions[handler][self.index]['function'] = function
            self.actions[handler][self.index]['args'] = function.__code__.co_argcount - 1
            print(f"+ set multi action for method: {str(self.index)}.) {handler} ({str(self.actions[handler][self.index]['args'])})")
            
        else:
            print("not function or method")
            return None

        self.index += 1
        return self.index - 1
        
    def remove_action(self, handler, function):
        if handler in self.actions:
            for nr, func_data in self.actions[handler].items():
                if func_data['function'] == function:
                    del self.actions[handler][nr]
                    return nr
 
    async def react (self, handler, *args):
        try:
            for index in self.actions[handler]:
                try: 
                    await self.actions[handler][index]['function'](*args[:self.actions[handler][index]['args']])
                except Exception as e:
                    print(f"error in opcode {handler}")
                    print(f"args: {args}")
                    print(e)
        except:
            pass
        
    def __defaultException(self, handler, message='handler not found!'):
        """
            The default Exception, should be replaced!
        """
        pass
        # return "EXCEPTION: " + handler +' '+ message
        
