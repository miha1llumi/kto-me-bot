import os
import unittest
from kto_me import SETTINGS_FOLDER, LOGS_FOLDER
from writer import create_folders, create_txt_files, ALL_TXT_FILES

PATH_TO_TEST_FOLDER = f"{os.getcwd()}/test_folder"


class TestFilesCreation(unittest.TestCase):
    def test_folders_creation(self):
        create_folders(path_to_folders=PATH_TO_TEST_FOLDER)

        self.assertTrue(os.path.isdir(f"{PATH_TO_TEST_FOLDER}/{LOGS_FOLDER}"))
        self.assertTrue(os.path.isdir(f"{PATH_TO_TEST_FOLDER}/{SETTINGS_FOLDER}"))

    def test_txt_files_creation(self):
        create_txt_files(path_to_folders=PATH_TO_TEST_FOLDER)

        self.assertTrue(os.path.exists(f"{PATH_TO_TEST_FOLDER}/{SETTINGS_FOLDER}/{ALL_TXT_FILES[0]}"))
        self.assertTrue(os.path.exists(f"{PATH_TO_TEST_FOLDER}/{SETTINGS_FOLDER}/{ALL_TXT_FILES[1]}"))
        self.assertTrue(os.path.exists(f"{PATH_TO_TEST_FOLDER}/{SETTINGS_FOLDER}/{ALL_TXT_FILES[2]}"))
        self.assertTrue(os.path.exists(f"{PATH_TO_TEST_FOLDER}/{SETTINGS_FOLDER}/{ALL_TXT_FILES[3]}"))
