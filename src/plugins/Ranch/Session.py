
import time
from framework import Opcodes as opcode


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
        self.running_sessions = {}  # 1 session per channel!
        self.closed_sessions = {}  # store only last session for one channel
        self.bot = bot
        
    def start_session(self, duration:int, channel_id:str=None, function=None):
        if channel_id not in self.running_sessions:
            self.running_sessions[channel_id] = Session(duration=duration, channel_id=channel_id, function=function)
            
            if self.bot and function and len(self.running_sessions) == 1:
                # register function!
                self.bot.opcodes_handler.add_action(opcode.CHANNEL_MESSAGE, function)
            
            # session started
            return True
        
        # no session started
        return False
            
    def is_channel(self, channel_id:str):
        if channel_id in self.running_sessions:
            return self.running_sessions[channel_id].channel_id == channel_id
        return False
    
    def has_session(self, channel_id):
        return channel_id in self.running_sessions
    
    def last_session(self, channel_id):
        if channel_id in self.closed_sessions:
            return self.closed_sessions[channel_id]
        return None
    
    def get_session(self, channel_id):
        if self.has_session(channel_id):
            return self.running_sessions[channel_id]
        return None
        
    def check_sessions(self):
        recently_closed = []
        
        for channel_id, session in self.running_sessions.items():
            if session.done(): 
                self.closed_sessions[channel_id] = self.running_sessions[channel_id]
                recently_closed.append(channel_id)
                
                # remove function from dispatch only if:
                # there is a bot
                # there are recently removed sessions
                # there are NO open sessions left
                if self.bot and any(recently_closed) and len(self.running_sessions) - len(recently_closed) == 0:
                    # print("remove function")
                    self.bot.opcodes_handler.remove_action(opcode.CHANNEL_MESSAGE, self.running_sessions[channel_id].function)
                    
        for channel_id in recently_closed:
            self.running_sessions.pop(channel_id)
        
        # return channels that are recently closed
        return recently_closed


def test():
    mgr = SessionManager()
    
    for _ in range(20):
        time.sleep(2)
        print(int(time.time()))
        print("Started 0" if mgr.start_session(6, 0) else "running")
        
        time.sleep(1)
        print(f"closed: {mgr.check_sessions()}")
        
        time.sleep(1)
        print("Started 1" if mgr.start_session(6, 1) else "running")
        
        time.sleep(1)      
        print(f"closed: {mgr.check_sessions()}")
        
    print(mgr.running_sessions)
    print(mgr.closed_sessions)
    
    print(mgr.has_session(0))
    print(mgr.last_session(1))

            
if __name__ == "__main__":
    test()
