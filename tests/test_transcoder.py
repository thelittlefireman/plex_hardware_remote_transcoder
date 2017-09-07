import os
import unittest

import master_transcoder

class TestInstall(TestCase):
    def test_remote_transcoder(self):
        self.assertTrue(master_transcoder.transcode())

    def test_remote_transcoder_no_server(self):
            self.assertFalse(master_transcoder.transcode())

    def test_remote_transcoder_password_noSSHPASS(self):
        self.assertTrue(master_transcoder.transcode(os.path.join("./tests/configTestNoPassword.json")))

    def test_remote_transcoder_password_sshpass(self):
        master_transcoder.transcode(os.path.join("./tests/configTestPassword.json"))
