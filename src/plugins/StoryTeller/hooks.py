

class Hooks:
    """
        Hooks that can be registered in the bot for the chat to interface with
        async functions only!
    """
    
    def __init__(self, story_teller=None):
        self.story_teller = story_teller 
        
    async def leaderboard(self):
        pass 
    
    async def start_session(self):
        pass 
    
    async def choice(self):
        """
        user input to make a choice for the session
        """
        pass
    
    async def end_ession(self):
        """
        user ends the session/session runs out
        """
        pass
    
    