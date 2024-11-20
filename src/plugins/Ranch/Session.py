
import time
from core import Opcodes  as opcode


class Session:
    
    def __init__(self, duration:int, channel_id:str=None, function=None):
        self.started = int(time.time())
        self.duration = duration
        self.channel_id = channel_id
        self.function = function
        self.storage = None
        
    def done(self):
        return int(time.time()) >= self.started + self.duration
        
    def __repr__(self):
        return f"Session(started={self.started} duration={self.duration})"
        
        
class SessionManager:
    
    def __init__(self, bot=None):
        self.running_session = None
        self.closed_sessions = []
        self.bot = bot
        
    def start_session(self, duration:int, function=None, channel_id:str=None):
        if not self.running_session:
            self.running_session = Session(duration=duration, channel_id=channel_id, function=function)
            
            if self.bot and function:
                # register function!
                self.bot.opcodes_handler.add_action(opcode.CHANNEL_MESSAGE, function)
            
    def is_channel(self, channel_id:str):
        if self.running_session:
            return self.running_session.channel_id == channel_id
        return False
        
    def check_session(self):
        if self.running_session and self.running_session.done():
            if self.bot:
                # unregister function!
                self.bot.opcodes_handler.remove_action(opcode.CHANNEL_MESSAGE, self.running_session.function)
                
            self.closed_sessions.append(self.running_session)
            self.running_session = None
            
            return True  # closed session
        
        return False  # no change


def test():
    mgr = SessionManager()
    for _ in range(10):
        time.sleep(1)
        print(int(time.time()))
        mgr.start_session(5)
        mgr.check_session()
        
    print(mgr.running_session, mgr.closed_sessions)

            
if __name__ == "__main__":
    test()
