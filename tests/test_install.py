"""Unit test to test app."""
import os,io
import unittest
from unittest import TestCase

import master_transcoder

TEST_FOLDER="./test folder/"
TEST_PATH=os.path.join(TEST_FOLDER,"Plex Transcoder")
class TestInstall(TestCase):
    """Unit test class to test other methods in the app."""
    def test_valid_install(self):
        if not os.path.exists(TEST_FOLDER):
            os.makedirs(TEST_FOLDER)
        with io.FileIO(TEST_PATH, "w") as file:
            file.write("Hello!")
            file.close()
        master_transcoder.install_phwrt()

"""   
   def test_valid_uninstall(self):
       master_transcoder.uninstall_phwrt()

   
   def test_install_on_install(self):
       master_transcoder.install_phwrt()
       master_transcoder.install_phwrt()

   
   def test_uninstall_before_install(self):
       master_transcoder.uninstall_phwrt()
"""