from plugins.Ranch.milkingstatus import MilkingStatus


class MilkJobResponse:
    
    def __init__(self, worker:str, cow:str, status:MilkingStatus=MilkingStatus.EMPTY, milk:int=0, amount:int=0, cow_lvl_up:bool=False, worker_lvl_up:bool=False):
        self.worker = worker
        self.cow = cow
        self.status = status
        
        self.max_milk = milk  # maximum milk possible
        
        self.amount = amount  # milked amout
        
        self.cow_lvl_up = cow_lvl_up
        self.worker_lvl_up = worker_lvl_up
