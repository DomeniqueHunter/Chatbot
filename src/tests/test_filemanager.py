#!/usr/bin/python3

import unittest, sys, os
sys.path.append('..')
from framework.lib.filemanager import FileManager


class TestData:

    def __init__(self, a):
        self.a = a

    def get_func(self):
        return self.a

    def set_func(self, a):
        self.a = a


def remove_file(file:str):
    if os.path.isfile(file):
        return os.remove(file)


def assertException(exception:Exception, expected_exception_type:str, expected_exception_message:str="") -> None:
    exception_type = exception.__class__
    exception_msg = str(exception)
    assert exception_type == expected_exception_type, f"Wrong Type! Expected '{expected_exception_type}' but received '{exception_type}'!"
    
    if expected_exception_message:
        assert exception_msg == expected_exception_message, f"Wrong Message! Expected: '{expected_exception_message}' but received '{exception_msg}'!"


class TestCase(unittest.TestCase):

    def setUp(self):
        self.fm = FileManager(".")

    def test_managed_file_save_load_func(self):
        print("Managed File save/load function")
        td = self.td = TestData('XXX')
        self.fm.add('test', 'test.txt', 'plain', td.get_func, td.set_func)

        test_string = "TEST X"
        self.td.a = test_string
        self.fm.save('test')
        check = self.fm.load('test')
        validate = check == test_string
        print(f"check: {check}")
        self.assertTrue(validate, f"{check} is expected to be '{test_string}'")

    def test_managed_file_save_load_content(self):
        print("Managed File given content")
        self.fm.add('test2', 'test2.txt', 'plain')

        test_string = "TEST Y"
        self.fm.save('test2', test_string)
        check = self.fm.load("test2")
        validate = check == test_string
        print(f"check: {check}")
        self.assertTrue(validate, f"{check} is expected to be '{test_string}'")

    def test_unmanaged_files(self):
        print("\nUnmanaged Files")

        test_string = "Schwabbel"
        self.fm.save_unmanaged_file("test3.txt", test_string)
        check = self.fm.load_unmanaged_file("test3.txt")
        validate = check == test_string
        print(f"check: {check}")
        self.assertTrue(validate, f"{check} is expected to be '{test_string}'")

    def test_managed_file_conflict(self):
        print("\nManaged File Conflict")
        self.fm.add('test4', 'test.txt', 'plain')

        test_string = "Schwabbel"
        try:
            self.fm.save_unmanaged_file("test.txt", "Schwabbel")
        except Exception as e:
            assertException(e, PermissionError, "Unable to write managed file: ./test.txt")

        try:
            check = self.fm.load_unmanaged_file("test.txt")
        except Exception as e:
            check = None
            assertException(e, PermissionError, "Unable to read managed file: ./test.txt")
            
        print(f"check: {check}")
        validate = check != test_string
        self.assertTrue(validate, f"{check} is expected to be '{test_string}'")

    def tearDown(self):
        print("Remove Managed Test Files")
        for mhandle, mfile in self.fm.managed_files.items():
            print(f"remove {mhandle} ({mfile.file_location})")
            remove_file(mfile.file_location)

        print("Remove Unanaged Test Files")
        remove_file("./test3.txt")


if __name__ == "__main__":
    unittest.main()  # run all tests
