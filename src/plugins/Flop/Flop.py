from plugins import PluginPrototype
from plugins.Flop.flop_session import FlopSession


class Flop(PluginPrototype):

    def __init__(self, client=None):
        self.module_name = "Flop Game"
        self.module_version = "1.0"
        self.client = client

        self.sessions = {}

    def set_client (self, client):
        self.client = client

    def is_current_session(self, channel):
        return channel in self.sessions

    async def start_session(self, user, channel):
        if not self.is_current_session(channel):
            self.sessions[channel] = FlopSession(user)
            message = "A new Flop was started, write !join to join the sessions! (Session ends in ~5min)\n"
            await self.client.send_public_message(message, channel)

        else:
            message = "there is already a flop sessions running"
            await self.client.send_public_message(message, channel)

    async def join_session(self, user, channel):
        if self.is_current_session(channel):
                if user not in self.sessions[channel].participants:
                    self.sessions[channel].join(user)
                    message = f"{user} joined the flop!"
                else:
                    message = f"{user} is already in the game!"

        else:
            message = f"no running flop sessions"

        await self.client.send_public_message(message, channel)
    async def end_session(self, channel):
        if len(self.sessions[channel].participants) > 1:
            self.sessions[channel].shuffle()
            message = f"All Participants flop their dicks at the same time:\n"
            message += f"{self.sessions[channel].participants[0]} wins\n"
            message += f"{self.sessions[channel].participants[-1]} loses\n\n"
            for nr, name in enumerate(self.sessions[channel].participants):
                message += f"{nr+1}. {name}\n"

        else:
            message = "sadly we had not enough participants for flop.."

        await self.client.send_public_message(message, channel)
        del self.sessions[channel]

    async def clock(self):
        for channel, session in self.sessions.items():
            if session.expired():
                await self.end_session(channel)

    def register_actions(self):
        if self.client:
            self.client.public_msg_handler.add_action("!flop", self.start_session, 'starts a game sessions', 'user', self.module_name)
            self.client.public_msg_handler.add_action("!join", self.join_session, 'join  a game sessions', 'user', self.module_name)
