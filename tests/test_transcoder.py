import os
from unittest import TestCase
import utilsphwrt
import master_transcoder

PARAMS1=['-codec:0' ,'h264' ,'-codec:1' ,'ac3' ,'-map_inlineass' ,'0:3' ,'-filter_complex' ,'[0:0]scale=w=1920:h=816[0];[0]format=pix_fmts=yuv420p|nv12[1];[1]inlineass=font_scale=1.000000:font_path=/usr/lib/plexmediaserver/Resources/Fonts/DejaVuSans-Regular.ttf:fontconfig_file=/usr/lib/plexmediaserver/Resources/fonts.conf[2]' ,'-map' ,'[2]' ,'-codec:0' ,'libx264' ,'-crf:0' ,'16' ,'-maxrate:0' ,'4503k' ,'-bufsize:0' ,'9006k' ,'-r:0' ,'23.975999999999999' ,'-preset:0' ,'veryfast' ,'-x264opts:0' ,'subme=0:me_range=4:rc_lookahead=10:me=dia:no_chroma_me:8x8dct=0:partitions=none' ,'-force_key_frames:0' ,'expr:gte(t0+n_forced*1)' ,'-map' ,'0:1' ,'-metadata:s:1' ,'language=fre' ,'-codec:1' ,'aac' ,'-ar:1' ,'48000' ,'-channel_layout:1' ,'stereo' ,'-b:1' ,'256k' ,'-segment_format' ,'mpegts' ,'-f' ,'ssegment' ,'-individual_header_trailer' ,'0' ,'-segment_time' ,'1' ,'-segment_start_number' ,'0' ,'-segment_copyts' ,'1' ,'-segment_time_delta' ,'0.0625' ,'-segment_list' ,'http://127.0.0.1:32400/video/:/transcode/session/bk1veixu4351ndrrlydjf823/0c5bcd82-20ce-4add-9f43-3d691db3ebca/seglist' ,'-segment_list_type' ,'csv' ,'-segment_list_size' ,'2147483647' ,'-max_delay' ,'5000000' ,'-avoid_negative_ts' ,'disabled' ,'-map_metadata' ,'-1' ,'-map_chapters' ,'-1' ,'media-%05d.ts' ,'-map' ,'0:3' ,'-f' ,'null' ,'-codec' ,'ass' ,'nullfile' ,'-start_at_zero' ,'-copyts' ,'-vsync' ,'cfr' ,'-y' ,'-nostats' ,'-loglevel' ,'verbose' ,'-loglevel_plex' ,'verbose' ,'-progressurl' ,'http://127.0.0.1:32400/video/:/transcode/session/bk1veixu4351ndrrlydjf823/0c5bcd82-20ce-4add-9f43-3d691db3ebca/progress']


class TestTranscoder(TestCase):
    def test_remote_transcoder(self):
        self.assertTrue(master_transcoder.transcode())

    def test_remote_transcoder_no_server(self):
        self.assertFalse(master_transcoder.transcode())

    def test_remote_transcoder_password_noSSHPASS(self):
        self.assertTrue(master_transcoder.transcode(os.path.join("./tests/configTestNoPassword.json")))

    def test_remote_transcoder_password_sshpass(self):
        master_transcoder.transcode(os.path.join("./tests/configTestPassword.json"))

    def test_local_transcoder_with_params(self):
        sys.argv=PARAMS1
        utilsphwrt.DEBUG=True
        master_transcoder.transcode(os.path.join("./tests/configTestPassword.json"))

