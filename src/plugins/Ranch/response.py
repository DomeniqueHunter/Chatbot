

class MilkJobResponse:
    
    def __init__(self, worker:str, cow:str, milk:int=0, amount:int=0, success:bool=False, cow_lvl_up:bool=False, worker_lvl_up:bool=False):
        self.worker = worker
        self.cow = cow
        self.max_milk = milk  # maximum milk possible
        
        self.amount = amount  # milked amout
        
        self.success = success
        self.cow_lvl_up = cow_lvl_up
        self.worker_lvl_up = worker_lvl_up
