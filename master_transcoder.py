#!/usr/bin/env python
import pipes
import subprocess

__author__  = "Thomas Goureau"
__version__ = "0.0.1"

import sys

import shutil
from utilsphwrt import *

""" Global Variable installation """
REMOTE_ARGS = (#"%(env)s;"
    "cd %(working_dir)s;"
    "%(command)s %(args)s")


def install_phwrt():
    # get path of remote transcode

    if not getPHWRTTranscoderPath():
        print "Couldn't find `phwrt-m-tr` executable"
        return False
    
    print "Rename old transcoder"
    # if already exist don't override
    if os.path.exists(getNewTranscoderPath()):
        print "Already Install, if is not working try override ?"
        return False

    # TODO if not found ==> already install
    
    try:
        os.rename(getOriginalTranscoderPath(), getNewTranscoderPath())
    except Exception, e:
        print "Error renaming original transcoder: %s" % str(e)
        print "path:" +getOriginalTranscoderPath()
        return False
    
    print "Replace by new transcoder"
    
    try:
        shutil.copyfile(getPHWRTTranscoderPath(), getOriginalTranscoderPath())
        os.chmod(getOriginalTranscoderPath(), 0755)
    except Exception,e:
        print "Error on installation: %s" % str(e)
        return False
    return True

def uninstall_phwrt():
    print "Rename new transcoder by old transcoder"
    
    if not os.path.exists(getNewTranscoderPath()):
        print "Couldn't find `local_plex_transcoder`, is phwrt installed ?"
        return False

    try:
        shutil.copyfile(getNewTranscoderPath(), getOriginalTranscoderPath())
        os.chmod(getOriginalTranscoderPath(), 0755)
    except Exception, e:
        print "Error on uninstall transcoder: %s" % str(e)
        return False
    if os.path.exists(getNewTranscoderPath()):
        os.remove(getNewTranscoderPath())
    return True
    #raise NotImplementedError("Not yet done please be patient ;)")

def transcode():
    config = get_config()
    # Set up the arguments
    args = [getNewTranscoderPath()] + sys.argv[1:]
    
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