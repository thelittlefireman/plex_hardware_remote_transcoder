#!/usr/bin/env python
import json
import os
import subprocess
import logging.config
from distutils.spawn import find_executable

import sys

DEBUG=None

# TODO change to be configurable by a file
# todo fix font parameters : /usr/lib/plexmediaserver/Resources/Fonts/
# extract from dpkg and change path
# change by reg exp for numbers
# if NOCHECK don't check second parameters just copy is
"""plexTranscoderChangeList = {
        "-map_inlineass" : "0:3",
        "-codec:0" : "libx264",
        "-crf:0" : "16",
        "-maxrate:0":"4503k",
        "-x264opts:0" :"NOCHECK",
        "-channel_layout:1" : "stereo",
        "-b:1":"256k",
        "-individual_header_trailer":"0",
        "-segment_copyts":"1",
        "-loglevel_plex":"verbose",
        "-progressurl":"NOCHECK"
}
ffmpegTranscoderChangeList = [
{"": ""},
{"-codec:0" : "cedrus264 -pix_fmt nv12"},
{"-crf": "16"},
{"-maxrate":"4503k"},
{"-x264-params:0" :"subme=0:me_range=4:rc_lookahead=10:me=dia:no_chroma_me:8x8dct=0:partitions=none"},
{"":""},
{"b:a":"256k"},
{"":""},
{"mpegts_copyts":"1"}
]"""
#????? -manifest_name http://127.0.0.1:32400/video/:/transcode/session/8frivkc33m10k3zrelaj5lsk/6ffe3670-ebe1-48f8-b326-b30e4bd0b94c/manifest
paramsToDelete=["-map_inlineass","-filter_complex","-map","-loglevel_plex","-fdash"]
paramsToChange=["-time_delta","-channel_layoutstereo","-skip_to_segment","-progressurl","ac3","libx264","h264","-crf:0","-maxrate:0","-bufsize:0","-r:0","-preset:0","-x264opts:0","-force_key_frames:0","-metadata:s:1","-metadata:s:0","aac","-ar:1","-channel_layout:1","-b:1","-segment_copyts","expr:gte(t0+n_forced*1)","ass"]
newParams=["-segment_time_delta","","-segment_start_number","-progress","copy","cedrus264 '-pix_fmt nv12'","cedrus264 '-pix_fmt nv12'","-crf","-maxrate","-bufsize","-r","-preset","-x264opts","-force_key_frames","-metadata:s:a","-metadata:s:v","copy","-ar","-channel_layout","-b:a","-mpegts_copyts","expr:gte(t,n_forced*1)","copy"]
#TODO subtitle : -vf subtitles=sub.srt:force_style='FontName=DejaVu Serif,FontSize=24' or ass codec



ffmpegAddArgs=["-hwaccel vdpau"]

DEFAULT_CONFIG = {
    "ipaddress": "",
    "path_script":    None,
    "servers_script": None,
    "transcode_path":None,
    "media_path":None,
    "servers":   {},
    "auth_token": None,
    "logging":   {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "filename": "/tmp/prt.log",
                "maxBytes": 10485760,
                "backupCount": 20,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "prt": {
                "level": "DEBUG",
                "handlers": ["file_handler"],
                "propagate": "no"
            }
        }
    }
}

log = logging.getLogger("prt")

ORIGINAL_TRANSCODER_NAME = "Plex Transcoder"
NEW_TRANSCODER_NAME = "local_plex_transcoder"
PHWRT_TRANSCODER_NAME = "phwrt-m-tr"

def get_config(path=None):
    if path == None:
        file_path =os.path.expanduser("~/.prt.conf")
    else:
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, path)
    try:
        log.info('Get config - '+file_path)
        return json.load(open(file_path))
    except Exception, e:
        if DEBUG:
            print ("Error load config: %s %s" % (str(e),str(path)))
        else:
            log.error("Error load config: %s %s" % (str(e),str(path)))
        log.info("Get config - DEFAULT_CONFIG")
        return DEFAULT_CONFIG.copy()

def convertAndFixParameter(config, args):
    # Check to see if we need to call a user-script to replace/modify the file path*
    if DEBUG:
        print 'before [%s]' % ', '.join(map(str, args))
    new_args=[]
    m_index = 0
    while m_index < len(args):
        v=args[m_index]
        # Convert plextranscoder arguments to ffmpeg
        if (v in paramsToDelete):
            m_index=m_index+2
        elif v == "-i" and config.get("path_script", None):
            # i+1 = real path /tmmtmtmtm/tltltl
            # Found the requested video path
            path = args[m_index+1]
            new_args.append(v)
            try:
                proc = subprocess.Popen([config.get("path_script"), path], stdout=subprocess.PIPE)
                proc.wait()
                new_path = proc.stdout.readline().strip()
                if new_path:
                    log.debug("Replacing path with: %s" % new_path)
                    new_args.append(new_path)
                else:
                     new_args.append(path)
            except Exception, e:
                log.error("Error calling path_script: %s" % str(e))
            m_index=m_index+2
        else:
            change =False
            for index, item in enumerate(paramsToChange):
                if (v == item):
                    new_args.append(newParams[index])
                    change =True
                    break
            if not change:
                new_args.append(v)
            m_index=m_index+1
            #TODO add some specifique arguments
            #ffmpegAddArgs
    if DEBUG:
        print 'after [%s]' % ', '.join(map(str, new_args))

    return new_args

def getTranscoderPath():
    if  DEBUG:
        TRANSCODER_PATH = "./test folder/"
    elif sys.platform == "darwin":
        # OS X
        TRANSCODER_PATH = "/Applications/Plex Media Server.app/Contents/"

    elif sys.platform.find('synology') != -1:
        # todo set by variable : volumeNum = raw_input("Volume Number: ")
        #synology
        TRANSCODER_PATH = "/volume1/@appstore/Plex Media Server/"

    elif sys.platform.startswith('linux'):
        # Linux
        TRANSCODER_PATH = "/usr/lib/plexmediaserver/"
    else:
        raise NotImplementedError("This platform is not yet supported")
    return TRANSCODER_PATH

def getSettingsPath():
    if DEBUG:
        SETTINGS_PATH = "./test folder/"
    elif sys.platform == "darwin":
        # OS X
        SETTINGS_PATH  = "~/Library/Preferences/com.plexapp.plexmediaserver"

    elif sys.platform.find('synology') != -1:
        # todo set by variable : volumeNum = raw_input("Volume Number: ")
        #synology
        SETTINGS_PATH  = "/volume1/Plex/Library/Application Support/Plex Media Server/Preferences.xml"

    elif sys.platform.startswith('linux'):
        # Linux
        SETTINGS_PATH  = "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Preferences.xml"
    else:
        raise NotImplementedError("This platform is not yet supported")
    return SETTINGS_PATH

def getOriginalTranscoderPath():
    return os.path.join(getTranscoderPath(),ORIGINAL_TRANSCODER_NAME)

def getNewTranscoderPath():
    return os.path.join(getTranscoderPath(),NEW_TRANSCODER_NAME)

def getPHWRTTranscoderPath():
    if DEBUG:
        return "./tests/phwrt_debug"
    else:
        return find_executable(PHWRT_TRANSCODER_NAME)

def setup_logging():
    config = get_config()
    logging.config.dictConfig(config["logging"])
#   if DEBUG:
    rootLog = logging.getLogger()
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    rootLog.addHandler(ch)


