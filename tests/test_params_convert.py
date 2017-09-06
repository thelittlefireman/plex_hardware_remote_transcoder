"""Unit test to test app."""
import os
import unittest
from unittest import TestCase
from utilsphwrt import *

import master_transcoder

PARAMS1=['-codec:0' ,'h264' ,'-codec:1' ,'ac3' ,'-map_inlineass' ,'0:3' ,'-filter_complex' ,'[0:0]scale=w=1920:h=816[0];[0]format=pix_fmts=yuv420p|nv12[1];[1]inlineass=font_scale=1.000000:font_path=/usr/lib/plexmediaserver/Resources/Fonts/DejaVuSans-Regular.ttf:fontconfig_file=/usr/lib/plexmediaserver/Resources/fonts.conf[2]' ,'-map' ,'[2]' ,'-codec:0' ,'libx264' ,'-crf:0' ,'16' ,'-maxrate:0' ,'4503k' ,'-bufsize:0' ,'9006k' ,'-r:0' ,'23.975999999999999' ,'-preset:0' ,'veryfast' ,'-x264opts:0' ,'subme=0:me_range=4:rc_lookahead=10:me=dia:no_chroma_me:8x8dct=0:partitions=none' ,'-force_key_frames:0' ,'expr:gte(t0+n_forced*1)' ,'-map' ,'0:1' ,'-metadata:s:1' ,'language=fre' ,'-codec:1' ,'aac' ,'-ar:1' ,'48000' ,'-channel_layout:1' ,'stereo' ,'-b:1' ,'256k' ,'-segment_format' ,'mpegts' ,'-f' ,'ssegment' ,'-individual_header_trailer' ,'0' ,'-segment_time' ,'1' ,'-segment_start_number' ,'0' ,'-segment_copyts' ,'1' ,'-segment_time_delta' ,'0.0625' ,'-segment_list' ,'http://127.0.0.1:32400/video/:/transcode/session/bk1veixu4351ndrrlydjf823/0c5bcd82-20ce-4add-9f43-3d691db3ebca/seglist' ,'-segment_list_type' ,'csv' ,'-segment_list_size' ,'2147483647' ,'-max_delay' ,'5000000' ,'-avoid_negative_ts' ,'disabled' ,'-map_metadata' ,'-1' ,'-map_chapters' ,'-1' ,'media-%05d.ts' ,'-map' ,'0:3' ,'-f' ,'null' ,'-codec' ,'ass' ,'nullfile' ,'-start_at_zero' ,'-copyts' ,'-vsync' ,'cfr' ,'-y' ,'-nostats' ,'-loglevel' ,'verbose' ,'-loglevel_plex' ,'verbose' ,'-progressurl' ,'http://127.0.0.1:32400/video/:/transcode/session/bk1veixu4351ndrrlydjf823/0c5bcd82-20ce-4add-9f43-3d691db3ebca/progress']
CORRECT_PARAMS1=['-codec:v' ,'cedrus264 -pix_fmt nv12','-codec:a' ,'copy' , '-codec:v' ,'cedrus264 -pix_fmt nv12','-crf','16','-maxrate' ,'4503k' ,'-bufsize' ,'9006k' ,'-r' ,'23.975999999999999' ,'-preset' ,'veryfast' ,'-x264opts' ,'subme=0:me_range=4:rc_lookahead=10:me=dia:no_chroma_me:8x8dct=0:partitions=none' ,'-force_key_frames' ,'expr:gte(t,n_forced*1)' ,'-metadata:s' ,'language=fre' ,'-codec:a' ,'copy' ,'-ar' ,'48000' ,'-channel_layout' ,'stereo' ,'-b:a' ,'256k' ,'-segment_format' ,'mpegts' ,'-f' ,'ssegment' ,'-individual_header_trailer' ,'0' ,'-segment_time' ,'1' ,'-segment_start_number' ,'0' ,'-mpegts_copyts' ,'1' ,'-segment_time_delta' ,'0.0625' ,'-segment_list' ,'http://127.0.0.1:32400/video/:/transcode/session/bk1veixu4351ndrrlydjf823/0c5bcd82-20ce-4add-9f43-3d691db3ebca/seglist' ,'-segment_list_type' ,'csv' ,'-segment_list_size' ,'2147483647' ,'-max_delay' ,'5000000' ,'-avoid_negative_ts' ,'disabled' ,'-map_metadata' ,'-1' ,'-map_chapters' ,'-1' ,'media-%05d.ts' ,'-f' ,'null' ,'-codec' ,'copy' ,'nullfile' ,'-start_at_zero' ,'-copyts' ,'-vsync' ,'cfr' ,'-y' ,'-nostats' ,'-loglevel' ,'verbose' ,'-progress' ,'http://127.0.0.1:32400/video/:/transcode/session/bk1veixu4351ndrrlydjf823/0c5bcd82-20ce-4add-9f43-3d691db3ebca/progress']

class TestConvertParams(TestCase):
    """Unit test class to test other methods in the app."""
    def test_convert_params_base(self):
        config = get_config()
        new_args = convertAndFixParameter(config,PARAMS1)
        self.assertEqual(CORRECT_PARAMS1,new_args)
    def test_correct_nb_params(self):
        self.assertEqual(len(newParams),len(paramsToChange))