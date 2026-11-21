
import time
from framework import opcode


class Session:

    def __init__(self, channel_id:str=None, duration:int=5, session_type:str="SESS", start_function=None, end_function=None):
        """
        @channel_id: identifier
        @duration: duration of session (min)
        @session_type: session type
        """
        self.started = int(time.time())
        self.duration = duration  # min
        self.end = self.started + duration
        self.channel_id = channel_id
        self.session_type = session_type
        self.session_id = f"{self.channel_id}_{self.session_type}"
        self.start_function = start_function
        self.end_function = end_function
        self.storage = None

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

    def __init__(self, bot=None):
        self.running_sessions = {}  # 1 session per channel!
        self.closed_sessions = {}  # store only last session for one channel
        self.bot = bot

    def start_session(self, channel_id:str=None, duration:int=5, session_type:str="SESS", start_function=None, end_function=None):
        """
        Starts a session for a channel with a timeout of duration. The session type shall be what ever string the starter sets
        to make the session unique for the channel.
        :channel_id:, str: id of the channel
        :duration, int: duration of session in seconds until timeout
        :session_type:, str: additional identifyer to allow multiple different sesssion per chanenl
        :start_function:, start_function:
        :end_function:,: end_function will be cakked after ending the session
        """
        session_id = f"{channel_id}_{session_type}"

        if session_id not in self.running_sessions:
            self.running_sessions[session_id] = Session(duration=duration, channel_id=channel_id, session_type=session_type, start_function=start_function, end_function=end_function)

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

    def is_channel(self, channel_id:str):
        if channel_id in self.running_sessions:
            return self.running_sessions[channel_id].channel_id == channel_id
        return False

    def has_session(self, channel_id, session_purpose:str="SESS"):
        session_id = f"{channel_id}_{session_purpose}"
        return session_id in self.running_sessions

    def last_session(self, channel_id:str, session_purpose:str="SESS"):
        session_id = f"{channel_id}_{session_purpose}"
        if session_id in self.closed_sessions:
            return self.closed_sessions[session_id]
        return None

    def get_session(self, channel_id, session_purpose:str="SESS"):
        session_id = f"{channel_id}_{session_purpose}"
        if self.has_session(channel_id, session_purpose):
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
    
    for _ in range(2):
        time.sleep(2)
        print(int(time.time()))
        print("Started 0" if mgr.start_session(_id, start_function=start_func, end_function=end_func) else "running")
        print("Started 0_1" if mgr.start_session(_id, 6, "1") else "running")

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
