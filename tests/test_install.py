"""Unit test to test app."""
import os,io
import unittest
from unittest import TestCase
from utilsphwrt import *
import master_transcoder

TEST_FOLDER="./test folder/"
TEST_PATH=os.path.join(TEST_FOLDER,"Plex Transcoder")

def beforeTest():
    utilsphwrt.DEBUG=True
    if not os.path.exists(TEST_FOLDER):
        os.makedirs(TEST_FOLDER)
    #create fake origin transcoder
    with io.FileIO(TEST_PATH, "w") as file:
        file.write("Hello!")
        file.close()
    #remove new transcode
    if os.path.exists(getNewTranscoderPath()):
        os.remove(getNewTranscoderPath())

class TestInstall(TestCase):
    """Unit test class to test other methods in the app."""
    def test_valid_install(self):
        beforeTest()
        self.assertTrue(master_transcoder.install_phwrt())
        self.assertTrue(os.path.exists(getNewTranscoderPath()))
        self.assertTrue(os.path.exists(getOriginalTranscoderPath()))
        self.assertTrue(os.path.exists(getPHWRTTranscoderPath()))

    def test_valid_uninstall(self):
        beforeTest()
        master_transcoder.install_phwrt()
        self.assertTrue(master_transcoder.uninstall_phwrt())
        self.assertFalse(os.path.exists(getNewTranscoderPath()))
        self.assertTrue(os.path.exists(getOriginalTranscoderPath()))
        self.assertTrue(os.path.exists(getPHWRTTranscoderPath()))


    def test_install_on_install(self):
        beforeTest()
        self.assertTrue(master_transcoder.install_phwrt())
        self.assertFalse(master_transcoder.install_phwrt())

    def test_uninstall_before_install(self):
        beforeTest()
        self.assertFalse(master_transcoder.uninstall_phwrt())

