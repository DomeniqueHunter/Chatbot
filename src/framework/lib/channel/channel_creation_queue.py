

class ChannelCreationQueue():
    
    
    def __init__(self):
        self.queue = []
        
    def add(self, channel_name:str, user:str, persistent:bool=False) -> None:
        self.queue.append({"name": channel_name, "user": user, "persistent": persistent})
        
    def pop(self, index:int=0) -> dict:
        return self.queue.pop(index)
    
    def size(self) -> int:
        return len(self.queue)