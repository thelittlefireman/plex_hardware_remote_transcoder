"""Unit test to test app."""
import os
import unittest
from unittest import TestCase

import master_transcoder

class TestInstall(TestCase):
    """Unit test class to test other methods in the app."""
    def test_valid_install(self):
        master_transcoder.install_phwrt()
        self.assertTrue(True)
    
    def test_valid_uninstall(self):
        master_transcoder.uninstall_phwrt()
        self.assertTrue(True)
    
    def test_install_on_install(self):
        master_transcoder.install_phwrt()
        master_transcoder.install_phwrt()
        self.assertTrue(True)
    
    def test_uninstall_before_install(self):
        master_transcoder.uninstall_phwrt()
        self.assertTrue(True)