

class ChannelCreationQueue():
    
    
    def __init__(self):
        self.queue = []
        
    def add(self, channel_name:str, user:str) -> None:
        self.queue.append({"name": channel_name, "user": user})
        
    def pop(self, index:int=0) -> dict:
        return self.queue.pop(index)
    
    def size(self) -> int:
        return len(self.queue)