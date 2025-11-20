from enum import Enum


class MilkingStatus(Enum):
    EMPTY = 0
    SUCCESS = 1
    FAILED = 2
    MILKED_ALREADY = 3
    MILKABLE_SOON = 4



def test():
    print(MilkingStatus.SUCCESS)
    print(MilkingStatus.FAILED)
    print(MilkingStatus.MILKED_ALREADY)
    print(MilkingStatus.MILKABLE_SOON)



if __name__ == "__main__":
    test()