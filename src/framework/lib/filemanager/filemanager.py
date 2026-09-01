
import os
import json
import pickle

from types import FunctionType, MethodType
from typing import Union


class ManagedFile:

    def __init__(self, handle:str, file_location:str, type:str,
                        get_function:Union[FunctionType, MethodType],
                        set_function:Union[FunctionType, MethodType]) -> None:
        self.handle = handle
        self.file_location = file_location
        self.get_function = get_function
        self.set_function = set_function
        self.type = type


class FileManager:

    def __init__(self, file_root:str) -> None:
        self.file_root = file_root

        # ensure dirs
        if not os.path.exists(self.file_root):
            os.makedirs(self.file_root, exist_ok=True)

        self.managed_files = {}

        # save/load functions
        self.save_functions = {
                        'plain': self.__save_plain,
                        'binary': self.__save_binary,
                        'json': self.__save_json
                        }

        self.load_functions = {
                        'plain': self.__load_plain,
                        'binary': self.__load_binary,
                        'json': self.__load_json
                        }

    def add(self, handle:str, file:str, type:str='json',
                    get_func:Union[FunctionType, MethodType]=None,
                    set_func:Union[FunctionType, MethodType]=None) -> ManagedFile | None:
        if handle not in self.managed_files:
            managed_file = ManagedFile(handle, os.path.join(self.file_root, file), type, get_func, set_func)
            self.managed_files[handle] = managed_file
            return managed_file
        return None

    def save(self, handle:str, content=None) -> None:
        try:
            m_file = self.managed_files[handle]
            if content == None:
                content = m_file.get_function()

            self.save_functions[m_file.type](m_file.file_location, content)

        except Exception as e:
            print(e)

    def load(self, handle:str) -> any:
        try:
            m_file = self.managed_files[handle]
            loaded_data = self.load_functions[m_file.type](m_file.file_location)
            if m_file.set_function:
                m_file.set_function(loaded_data)
            return loaded_data

        except Exception as e:
            print(e)

        return None

    def save_all(self) -> None:
        for handle in self.managed_files.keys():
            self.save(handle)

    def load_all(self) -> None:
        for handle in self.managed_files.keys():
            self.load(handle)

    # TODO:
    # unmanaged files: maybe we can make this a little more general
    # to be able to store all kinds of general files and not just plain text
    def __check_file_conflict(self, tfile) -> bool:
        """
        check if files are in conflict or not.
        returns True if all is clear and False if files are in conflict with managed files
        """
        for mhandle, mfile in self.managed_files.items():
            if mfile.file_location == tfile:
                return False

        return True

    def save_unmanaged_file(self, filename:str, content:str) -> None:
        tfile = os.path.join(self.file_root, filename)
        if self.__check_file_conflict(tfile):
            self.__save_plain(tfile, content)
        else:
            # TODO: raise exception
            print("file conflict")
            raise PermissionError(f"Unable to write managed file: {tfile}")

    def load_unmanaged_file(self, filename:str) -> str:
        tfile = os.path.join(self.file_root, filename)
        if self.__check_file_conflict(tfile):
            return self.__load_plain(tfile)
        else:
            # TODO: raise exception
            print("file conflict")
            raise PermissionError(f"Unable to read managed file: {tfile}")

    def __save_plain(self, f_location, content) -> None:
        with open(f_location, 'w') as fp:
            fp.write(content)

    def __save_binary(self, f_location, content) -> None:
        with open(f_location, 'wb') as fp:
            pickle.dump(content, fp)

    def __save_json(self, f_location, content) -> None:
        with open(f_location, 'w') as fp:
            json.dump(content, fp, indent=4)

    def __load_plain(self, f_location) -> str:
        with open(f_location, 'r') as fp:
            return fp.read()

    def __load_binary(self, f_location) -> any:
        with open(f_location, 'rb') as fp:
            return pickle.load(fp)

    def __load_json(self, f_location) -> any:
        with open(f_location, 'r') as fp:
            return json.load(fp)


def test():

    print("Test in tests dir")


if __name__ == "__main__":
    test()
