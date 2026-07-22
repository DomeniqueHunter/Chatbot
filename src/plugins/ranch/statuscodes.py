from enum import Enum


class MilkingStatus(Enum):
    EMPTY = 0
    SUCCESS = 1
    FAILED = 2
    MILKING_DONE_TODAY = 3
    MILKING_ON_COOLDOWN = 4
    COW_EMPTY = 5
    
    
class PersonStatus(Enum):
    NONE = None
    IS_COW = 1
    ALREADY_COW = 11
    NEW_COW = 12
    IS_WORKER = 2
    ALREADY_WORKER = 21
    NEW_WORKER = 22


def test():
    print(MilkingStatus.SUCCESS)
    print(MilkingStatus.FAILED)
    print(MilkingStatus.MILKING_DONE_TODAY)
    print(MilkingStatus.MILKING_ON_COOLDOWN)
    
    print(PersonStatus.NONE)


if __name__ == "__main__":
    test()
