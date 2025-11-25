from typing import Any, Union
import time


class Timeout:

    def __init__(self):
        self.__timeouts = {}

    def set(self, key:Any, value:Union[int, None]=None) -> None:
        """
        Stores a timestamp for a given key.
        If value is None, the current epoch time is used.

        :key: identifier for the timeout entry
        :value: epoch timestamp or None
        """
        value = int(time.time()) if value is None else value
        self.__timeouts[key] = value
    
    def add(self, key:Any, value:Union[int, None]=None) -> None:
        return self.set(key, value)

    def check(self, key:Any, timeout_s:int=3600) -> bool:
        """
        Determines whether the timeout for a key has passed.
        Returns True if no timeout exists or if the stored time
        is older than timeout_s seconds.

        :key: identifier to check
        :timeout_s: timeout duration in seconds
        :return: True if expired or missing, False otherwise
        """
        now = int(time.time())
        last = self.__timeouts.get(key, 0)
        return (now - last) >= timeout_s

    def get(self, key:Any) -> int:
        """
        Retrieves the stored timestamp for a key.
        Returns 0 if the key is not present.

        :key: identifier to read
        :return: epoch timestamp or 0
        """
        return self.__timeouts.get(key, 0)

    def remove(self, key:Any) -> bool:
        """
        Removes the timeout entry for a key.
        Returns True if the entry existed, False otherwise.

        :key: identifier to remove
        :return: boolean
        """
        item = self.__timeouts.pop(key, None)
        return item is not None
    
    def get_timeouts(self) -> dict:
        return self.__timeouts
    
    def set_timeouts(self, timeouts:dict):
        self.__timeouts = timeouts


def test() -> None:
    timeout = Timeout()
    key_1 = ("A", "B")

    if timeout.check(key_1, 3):
        print("1 No timeout exists")
        timeout.set(key_1)
        print(timeout.get(key_1))

    time.sleep(2)

    if timeout.check(key_1, 3):
        print("2 No timeout exists")
        timeout.set(key_1)
        print(timeout.get(key_1))
    else:
        print("2 On Timeout!")

    time.sleep(1)

    if timeout.check(key_1, 3):
        print("3 No timeout exists")
        timeout.remove(key_1)
        print(timeout.get(key_1))
    else:
        print("3 On Timeout!")


if __name__ == "__main__":
    test()
