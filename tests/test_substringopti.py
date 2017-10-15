import os, sys
from unittest import TestCase
import utilsphwrt
import master_transcoder
def beforeTest():
    utilsphwrt.DEBUG=True
class TestTranscoder(TestCase):


    def test_substringopti(self):
        beforeTest()
        master_transcoder.subtring_optimisation()