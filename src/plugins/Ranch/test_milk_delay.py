

from plugins.Ranch.Logic import Logic
import time


def test():
    l = Logic(None)
    
    worker = "Worker1"
    cow = "Cow1"
    
    l.worker_interactions[worker][cow] = int(time.time())
    
    time.sleep(1)
    
    if l.check_milking_delay(worker, cow, 2):
        print("ready again")
    
    else:
        print("wait some more")
    
    worker2 = "Worker2"
    if l.check_milking_delay(worker2, cow, 2):
        print(f"{worker2} milked {cow}")
        l.worker_interactions[worker2][cow] = int(time.time())
    
    else:
        print("wait for it")
    
    if l.check_milking_delay(worker2, cow, 2):
        print(f"{worker2} milked {cow}")
        l.worker_interactions[worker2][cow] = int(time.time())
    
    else:
        print("wait for it")
    
    time.sleep(3)    
    
    if l.check_milking_delay(worker2, cow, 2):
        print(f"{worker2} milked {cow}")
        l.worker_interactions[worker2][cow] = int(time.time())
    
    else:
        print("wait for it")


if __name__ == "__main__":
    test()
