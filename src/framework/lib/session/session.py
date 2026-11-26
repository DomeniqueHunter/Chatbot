
import time
from framework import opcode
from dataclasses import dataclass


@dataclass
class SessionData:
    """Base class for all session data objects."""


class Session:

    def __init__(self, channel_id:str=None, timeout:int=5, *, session_type:str="SESS", session_data:SessionData=None, start_function=None, end_function=None):
        """
        @channel_id: identifier
        @timeout: timeout of session
        @session_type: session type
        """
        self.started = int(time.time())
        self.duration = timeout
        self.end = self.started + timeout
        self.channel_id = channel_id
        self.session_type = session_type
        self.session_id = f"{self.channel_id}_{self.session_type}"
        self.start_function = start_function
        self.end_function = end_function
        self.storage = session_data

    def extend(self, duration:int=None):
        """
        extends session fod duration seconds, if duration is none, take default duration of class
        duration int, (optional): session will be porolonged for duration seconds
        """
        if duration:
            self.end += duration
        else:
            self.end += self.duration

    def done(self) -> bool:
        """
        checks if session is done, return True if session is over, False if session continues
        """
        return int(time.time()) >= self.end

    def __repr__(self):
        return f"Session(started={self.started} duration={self.duration})"


class SessionManager:

    def __init__(self):
        self.running_sessions = {}  # 1 session per channel!
        self.closed_sessions = {}  # store only last session for one channel

    def start_session(self, channel_id:str=None, timeout:int=5, *, session_type:str="SESS", session_data:SessionData=None,start_function=None, end_function=None):
        """
        Starts a session for a channel with a timeout of timeout. The session type shall be what ever string the starter sets
        to make the session unique for the channel.
        :channel_id:, str: id of the channel
        :timeout, int: timeout of session in seconds until timeout
        :session_type:, str: additional identifyer to allow multiple different sesssion per chanenl
        :start_function:, start_function:
        :end_function:,: end_function will be cakked after ending the session
        """
        session_id = f"{channel_id}_{session_type}"

        if session_id not in self.running_sessions:
            session = Session(channel_id=channel_id, 
                              timeout=timeout, 
                              session_type=session_type, 
                              session_data=session_data, 
                              start_function=start_function, 
                              end_function=end_function)
            self.running_sessions[session_id] = session

            if start_function and len(self.running_sessions) == 1:
                # register function!
                # TODO: start_function args ?
                session = self.running_sessions.get(session_id, None)
                if session and callable(getattr(session, "start_function", None)):
                    session.start_function()
                else:
                    print ("NEIN")
                    exit()

            # session started
            return True

        # no session started
        return False

    def has_session(self, channel_id, session_type:str="SESS") -> bool:
        session_id = f"{channel_id}_{session_type}"
        return session_id in self.running_sessions

    def last_session(self, channel_id:str, session_type:str="SESS") -> Session|None:
        session_id = f"{channel_id}_{session_type}"
        if session_id in self.closed_sessions:
            return self.closed_sessions[session_id]
        return None

    def get_session(self, channel_id, session_type:str="SESS") -> Session|None:
        session_id = f"{channel_id}_{session_type}"
        if self.has_session(channel_id, session_type):
            return self.running_sessions[session_id]
        return None

    def check_sessions(self):
        recently_closed = []

        for session_id, session in self.running_sessions.items():
            if session.done():
                self.closed_sessions[session_id] = self.running_sessions[session_id]
                recently_closed.append(session_id)

                # remove function from dispatch only if:
                # there is a bot
                # there are recently removed sessions
                # there are NO open sessions left
                if any(recently_closed) and len(self.running_sessions) - len(recently_closed) == 0:
                    # print("remove function")
                    if callable(getattr(session, "end_function", None)):
                        # TODO: end_function args ?
                        session.end_function()

        for session_id in recently_closed:
            self.running_sessions.pop(session_id)

        # return channels that are recently closed
        return recently_closed


def test():
    mgr = SessionManager()

    _id = "ID"
    
    def start_func():
        print("START FUNCTION")
        
    def end_func():
        print("END FUNCTION")
    
    class Data(SessionData):
        x = 0
        
    data = Data()
    
    for _ in range(3):
        time.sleep(2)
        print(int(time.time()))
        print(f"Started {_id}_SESS" if mgr.start_session(_id, session_data=data, start_function=start_func, end_function=end_func) else "running")
        print(f"Started {_id}_SEZZ" if mgr.start_session(_id, 6, session_type="SEZZ") else "running")

        time.sleep(1)
        print(f"closed: {mgr.check_sessions()}")

        time.sleep(1)
        print("Started 1" if mgr.start_session(6, 1) else "running")
        data.x += 1

        time.sleep(1)
        print(f"closed: {mgr.check_sessions()}")

    print(mgr.running_sessions)
    print(mgr.closed_sessions)

    print(mgr.has_session(0))
    print(mgr.last_session(1))
    
    sess = mgr.get_session(_id, "SESS")
    print(sess.storage.x)


if __name__ == "__main__":
    test()
