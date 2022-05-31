

class ChannelCreationQueue():
    
    
    def __init__(self):
        self.queue = []
        
    def add(self, channel_name, user):
        self.queue.append({"name": channel_name, "user": user})
        
    def pop(self, index=0):
        return self.queue.pop(index)
    
    def size(self):
        return len(self.queue)