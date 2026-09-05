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
        print(f" - remove {file}")
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
        self.files_to_delete = []
        print()

    def test_managed_file_save_load_func(self):
        print("Managed File save/load function")
        td = self.td = TestData('XXX')
        self.fm.add('test', 'test1.txt', 'plain', td.get_func, td.set_func)

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
        print("Unmanaged Files")

        test_string = "Schwabbel"
        filename = "test3.txt"
        self.files_to_delete.append(filename)
        self.fm.save_unmanaged_file(filename, test_string, "plain")
        check = self.fm.load_unmanaged_file(filename, "plain")
        validate = check == test_string
        print(f"check: {check}")
        self.assertTrue(validate, f"{check} is expected to be '{test_string}'")

    def test_managed_file_conflict(self):
        print("Managed File Conflict")
        self.fm.add('test4', 'test4.txt', 'plain')

        test_string = "Schwabbel"
        try:
            self.fm.save_unmanaged_file("test4.txt", "Schwabbel", "plain")
        except Exception as e:
            assertException(e, PermissionError, "Unable to write managed file: ./test4.txt")

        try:
            check = self.fm.load_unmanaged_file("test4.txt", "plain")
        except Exception as e:
            check = None
            assertException(e, PermissionError, "Unable to read managed file: ./test4.txt")

        print(f"check: {check}")
        validate = check != test_string
        self.assertTrue(validate, f"{check} is expected to be '{test_string}'")

    def test_unmanaged_file_hash(self):
        print("Unmanaged File Hash")
        filename = "test5.txt"
        self.files_to_delete.append(filename)
        self.fm.save_unmanaged_file(filename, "test", "plain")
        hash_clear = self.fm.unmanaged_file_hash(filename)
        self.assertEqual("9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", hash_clear, f"hash values are not equal")

    def test_unmanaged_file_hash_not_exists(self):
        print("Unmanaged File Hash Does not exist")
        filename = "test6.txt"
        self.files_to_delete.append(filename)
        hash_clear = self.fm.unmanaged_file_hash(filename)
        self.assertEqual("", hash_clear, f"file has can not exist thus the has must be empty")

    def test_hash_managed_file(self):
        print("Managed File Hash")
        filename = "test7.txt"
        self.fm.add('test7', filename, 'plain')

        test_string = "TEST XXX"
        self.fm.save('test7', test_string)
        hash_clear = self.fm.hash("test7")
        print(hash_clear)
        print(self.fm.load("test7"))

        self.assertEqual("3cfff94b4f67e4b9f7869bc163c7da5cea9b1a4f9bed109796cb194ae75376b4", hash_clear, "hash values are not equal")

    def test_save_unmanaged_json(self):
        print("Unmanaged File JSON")
        filename = "test6.json"
        self.files_to_delete.append(filename)
        data = {"a": 1}
        self.fm.save_unmanaged_file(filename, data, "json")
        
        r_data = self.fm.load_unmanaged_file(filename, "json")
        self.assertEqual(data, r_data, "data is not the same")
        
    def test_save_unmanaged_json_complex_data(self):
        print("Unmanaged File JSON Complex Data")
        filename = "test7.json"
        self.files_to_delete.append(filename)
        data = {
            "a": 1,
            "b": [1,2,3],
        }
        self.fm.save_unmanaged_file(filename, data, "json")
        
        r_data = self.fm.load_unmanaged_file(filename, "json")
        self.assertEqual(data, r_data, "data is not the same")

    def tearDown(self):
        if self.fm.managed_files:
            print("# Remove Managed Test Files")
            for mhandle, mfile in self.fm.managed_files.items():
                print(f" - remove {mhandle} ({mfile.file_location})")
                remove_file(mfile.file_location)
        
        if len(self.files_to_delete) > 0:
            print("# Remove Unanaged Test Files")
            for file in self.files_to_delete:
                remove_file(file)


if __name__ == "__main__":
    unittest.main()  # run all tests
