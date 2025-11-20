from enum import Enum


class MilkingStatus(Enum):
    EMPTY = 0
    SUCCESS = 1
    FAILED = 2
    MILKING_DONE_TODAY = 3
    MILKING_ON_COOLDOWN = 4



def test():
    print(MilkingStatus.SUCCESS)
    print(MilkingStatus.FAILED)
    print(MilkingStatus.MILKING_DONE_TODAY)
    print(MilkingStatus.MILKING_ON_COOLDOWN)



if __name__ == "__main__":
    test()