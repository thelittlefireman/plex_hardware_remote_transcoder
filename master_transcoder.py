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

def prepare_nfs(configPath=None):
    if configPath == None:
        config = get_config()
    else:
        config = get_config(configPath)

    servers = config["servers"]
    selected_hostname, selected_host = None, None
    # TODO add loadBalancing # host["port"], host["user"]
    for hostname, host in servers.items():
        selected_hostname= hostname
        selected_host=host

    if config["transcode_path"] != None:
        #edit /etc/exports /home/user2 192.168.0.11(rw,sync)
        transcode_mount_path = config["transcode_path"]+" "+selected_host+"(rw,sync)"
        if not transcode_mount_path in open('/etc/exports').read():
            with open("/etc/exports", "a") as f:
                f.write(transcode_mount_path)
                f.close

    if config["media_path"] != None:
        media_mount_path = config["media_path"]+" "+selected_hostname+"(rw,sync)"
        if not media_mount_path in open('/etc/exports').read():
            with open("/etc/exports", "a") as f:
                f.write(media_mount_path)
                f.close

    allow_server = "ALL:"+selected_hostname
    if not allow_server in open('/etc/hosts.allow').read():
        with open("/etc/hosts.allow", "a") as f:
            f.write(allow_server)
            f.close

    deny_server = "ALL:PARANOID"
    if not deny_server in open('/etc/hosts.deny').read():
        with open("/etc/hosts.deny", "a") as f:
            f.write(deny_server)
            f.close

    nfs = subprocess.Popen("systemctl restart nfs-kernel-server")
    nfs.wait()




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

def transcode(configPath=None):
    if configPath == None:
        config = get_config()
    else:
        config = get_config(configPath)
    # Set up the arguments
    #original transcode path args = [getNewTranscoderPath()] + sys.argv[1:]
    #args = ['ffmpeg'] + sys.argv[1:]
    # get serveurs list
    servers = config["servers"]

    selected_hostname, selected_host = None, None
    # TODO add loadBalancing # host["port"], host["user"]
    for hostname, host in servers.items():
        selected_hostname= hostname
        selected_host=host

    if selected_host == None or selected_host == None:
        print "can't select server"
        log.error("can't select server")
        return False
    args = convertAndFixParameter(config, args)
            
    command = REMOTE_ARGS % {
        #"env":          build_env(),
        "working_dir":  pipes.quote(os.getcwd()),
        "command":      "ffmpeg",
        "args":         ' '.join([pipes.quote(a) for a in args])
    }
    log.info("Launching transcode_remote with command %s\n" % command)

    if "password" in selected_host and (selected_host["password"]!="" or selected_host["password"]!= None):
        if not find_executable("sshpass"):
            print "To use ssh with password auth you should install sshpass first"
            return False
        args = ["sshpass", "-p", "%s" % selected_host["password"],"ssh", "-tt", "-R", "32400:127.0.0.1:32400", "%s@%s" % (selected_host["user"], selected_hostname), "-p", selected_host["port"]]
    else:
        if not find_executable("ssh"):
            print "To use ssh you should install ssh first"
            return False
        args = ["ssh", "-tt", "-R", "32400:127.0.0.1:32400", "%s@%s" % (selected_host["user"], selected_hostname), "-p", selected_host["port"]]

    args = args + [command]

    if DEBUG:
        print ("Launching transcode_remote with args %s\n" % args)
    else:
        log.info("Launching transcode_remote with args %s\n" % args)

    # Spawn the process
    try:
        proc = subprocess.Popen(args)
        proc.wait()
    except ValueError, e:
        print e.output
        log.error(e.output)
        proc.kill()

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

    if sys.argv[1] == "prepare_nfs":
        print "prepare server for nfs mount"
        prepare_nfs()

def usage():
    return ""