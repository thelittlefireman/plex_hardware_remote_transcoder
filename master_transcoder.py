#!/usr/bin/env python
__author__  = "Thomas Goureau"
__version__ = "0.0.1"

import sys
import os

from distutils.spawn import find_executable

DEBUG=True

""" Global Variable installation """
if sys.platform == "darwin":
# OS X
    TRANSCODER_DIR = "/Applications/Plex Media Server.app/Contents/"
    SETTINGS_PATH  = "~/Library/Preferences/com.plexapp.plexmediaserver"

elif sys.platform.find('synology') != -1:
    # todo set by variable : volumeNum = raw_input("Volume Number: ")
    #synology
    TRANSCODER_DIR = "/volume1/@appstore/Plex Media Server"
    SETTINGS_PATH  = "/volume1/Plex/Library/Application Support/Plex Media Server/Preferences.xml"

elif sys.platform.startswith('linux'):
    # Linux
    TRANSCODER_DIR = "/usr/lib/plexmediaserver/"
    SETTINGS_PATH  = "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Preferences.xml"
elif DEBUG:
    TRANSCODER_DIR = "./testFolder"
else:
    raise NotImplementedError("This platform is not yet supported")
    
# 
ORIGINAL_TRANSCODER_NAME = TRANSCODER_DIR+"Plex Transcoder"
NEW_TRANSCODER_NAME = TRANSCODER_DIR+"local_plex_transcoder"
PHWRT_TRANSCODER_NAME = "phwrt-m-tr"

ORIGINAL_TRANSCODER_PATH = TRANSCODER_DIR+ORIGINAL_TRANSCODER_NAME
NEW_TRANSCODER_PATH = TRANSCODER_DIR+NEW_TRANSCODER_NAME
PHWRT_TRANSCODER_PATH= find_executable(PHWRT_TRANSCODER_NAME)

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

paramsToDelete=["-map_inlineass","-filter_complex","-map","-loglevel_plex"]
paramsToChange=["-progressurl","-codec:1","-codec:0","ac3","libx264","h264","-crf:0","-maxrate:0","-bufsize:0","-r:0","-preset:0","-x264opts:0","-force_key_frames:0","-metadata:s:1","aac","-ar:1","-channel_layout:1","-b:1","-segment_copyts","expr:gte(t0+n_forced*1)","ass"]
newParams=["-progress","-codec:a","-codec:v","copy","cedrus264 -pix_fmt nv12","cedrus264 -pix_fmt nv12","-crf","-maxrate","-bufsize","-r","-preset","-x264opts","-force_key_frames","-metadata:s","copy","-ar","-channel_layout","-b:a","-mpegts_copyts","expr:gte(t,n_forced*1)","copy"]
#TODO subtitle : -vf subtitles=sub.srt:force_style='FontName=DejaVu Serif,FontSize=24' or ass codec

REMOTE_ARGS = (#"%(env)s;"
               "cd %(working_dir)s;"
               "%(command)s %(args)s")

ffmpegAddArgs=["-hwaccel vdpau"]


DEFAULT_CONFIG = {
    "ipaddress": "",
    "path_script":    None,
    "servers_script": None,
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
                "level": "INFO",
                "formatter": "simple",
                "filename": "/tmp/prt.log",
                "maxBytes": 10485760,
                "backupCount": 20,
                "encoding": "utf8"
            },
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

def get_config():
    path = os.path.expanduser("~/.prt.conf")
    try:
        return json.load(open(path))
    except Exception, e:
        return DEFAULT_CONFIG.copy()

def install_phwrt():
    # get path of remote transcode

    if not PHWRT_TRANSCODER_PATH:
        print "Couldn't find `phwrt-m-tr` executable"
        return
    
    print "Rename old transcoder"
    # TODO if already exist don't override
    # TODO if not found ==> already install
    
    try:
        os.rename(ORIGINAL_TRANSCODER_PATH, NEW_TRANSCODER_PATH)
    except Exception, e:
        print "Error renaming original transcoder: %s" % str(e)
        return False
    
    print "Replace by new transcoder"
    
    try:
        shutil.copyfile(phwrt-m-tr, ORIGINAL_TRANSCODER_PATH)
        os.chmod(os.path.join(TRANSCODER_DIR,NEW_TRANSCODER_NAME), 0755)
    except Exception,e:
        print "Error on installation"

def uninstall_phwrt():
    print "Rename new transcoder by old transcoder"
    
    if not os.path.exists(NEW_TRANSCODER_PATH):
        print "Couldn't find `local_plex_transcoder`, is phwrt installed ?"
        return
    try:
        shutil.copyfile(NEW_TRANSCODER_PATH, ORIGINAL_TRANSCODER_PATH)
        os.chmod(os.path.join(TRANSCODER_DIR,ORIGINAL_TRANSCODER_NAME), 0755)
    except Exception, e:
        print "Error on uninstall transcoder: %s" % str(e)
        return False
    #raise NotImplementedError("Not yet done please be patient ;)")

def transcode():
    config = get_config()
    # Set up the arguments
    args = [local_transcodepath] + sys.argv[1:]
    
    # get serveurs list
    servers = config["servers"]

    selected_hostname, selected_host = None, None
    # TODO add loadBalancing # host["port"], host["user"]
    for hostname, host in servers.items():
        selected_hostname= hostname
        selected_host=host
    
    args = convertAndFixParameter(config, args)
            
    command = REMOTE_ARGS % {
        #"env":          build_env(),
        "working_dir":  pipes.quote(os.getcwd()),
        "command":      PHWRT_TRANSCODER_NAME,
        "args":         ' '.join([pipes.quote(a) for a in args])
    }
    log.info("Launching transcode_remote with command %s\n" % command)
    
    args = ["ssh", "-tt", "-R", "32400:127.0.0.1:32400", "%s@%s" % (host["user"], hostname), "-p", host["port"]] + [command]


    log.info("Launching transcode_remote with args %s\n" % args)

    # Spawn the process
    proc = subprocess.Popen(args)
    proc.wait()

    log.info("Transcode stopped on host '%s'" % hostname)

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
        if v == "-i" and config.get("path_script", None):
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

def main():
    # Specific usage options
    if len(sys.argv) < 2 or any((sys.argv[1] == "usage", sys.argv[1] == "help", sys.argv[1] == "-h",
            sys.argv[1] == "?",)):
        usage()
        sys.exit(-1)
    
    if sys.argv[len(sys.argv)] == "-d" or sys.argv[len(sys.argv)] == "debug":
        DEBUG=True
        TRANSCODER_DIR = "./testFolder"
    
    if sys.argv[1] == "install":
        print "Installing Plex hardware remote Transcoder"
        install_phwrt()

    if sys.argv[1] == "uninstall":
        print "Uninstalling Plex hardware remote Transcoder"
        uninstall_phwrt()