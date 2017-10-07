#!/usr/bin/env python
import pipes
import subprocess
from distutils.spawn import find_executable
__author__  = "Thomas Goureau"
__version__ = "0.0.1"

import sys,os

import shutil
import utilsphwrt

""" Global Variable installation """
REMOTE_ARGS = (#"cd %(working_dir)s;"
    "%(command)s %(args)s")


def install_phwrt():
    # get path of remote transcode

    #generate config
    utilsphwrt.get_config()

    if not utilsphwrt.getPHWRTTranscoderPath():
        print "Couldn't find `phwrt-m-tr` executable"
        return False
    
    print "Rename old transcoder"
    # if already exist don't override
    if os.path.exists(utilsphwrt.getNewTranscoderPath()):
        print "Already Install, if is not working try override ?"
        return False

    # TODO if not found ==> already install
    
    try:
        os.rename(utilsphwrt.getOriginalTranscoderPath(), utilsphwrt.getNewTranscoderPath())
    except Exception, e:
        print "Error renaming original transcoder: %s" % str(e)
        print "path:" +utilsphwrt.getOriginalTranscoderPath()
        return False
    
    print "Replace by new transcoder"
    
    try:
        shutil.copyfile(utilsphwrt.getPHWRTTranscoderPath(), utilsphwrt.getOriginalTranscoderPath())
        os.chmod(utilsphwrt.getOriginalTranscoderPath(), 0755)
    except Exception,e:
        print "Error on installation: %s" % str(e)
        return False
    return True

def prepare_nfs(configPath=None):
    if configPath == None:
        config = utilsphwrt.get_config()
    else:
        config = utilsphwrt.get_config(configPath)

    servers = config["servers"]
    selected_hostname, selected_host = None, None
    # TODO add loadBalancing # host["port"], host["user"]
    for hostname, host in servers.items():
        selected_hostname= hostname
        selected_host=host

    if config["transcode_path"] != None:
        #edit /etc/exports /home/user2 192.168.0.11(rw,sync)
        transcode_mount_path = str(config["transcode_path"])+" "+str(selected_host)+"(rw,sync)"
        if not transcode_mount_path in open('/etc/exports').read():
            with open("/etc/exports", "a") as f:
                f.write(transcode_mount_path)
                f.close

    if config["media_path"] != None:
        media_mount_path = str(config["media_path"])+" "+str(selected_hostname)+"(rw,sync)"
        if not media_mount_path in open('/etc/exports').read():
            with open("/etc/exports", "a") as f:
                f.write(media_mount_path)
                f.close

    allow_server = "ALL:"+str(selected_hostname)
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
    
    if not os.path.exists(utilsphwrt.getNewTranscoderPath()):
        print "Couldn't find `local_plex_transcoder`, is phwrt installed ?"
        return False

    try:
        shutil.copyfile(utilsphwrt.getNewTranscoderPath(), utilsphwrt.getOriginalTranscoderPath())
        os.chmod(utilsphwrt.getOriginalTranscoderPath(), 0755)
    except Exception, e:
        print "Error on uninstall transcoder: %s" % str(e)
        return False
    if os.path.exists(utilsphwrt.getNewTranscoderPath()):
        os.remove(utilsphwrt.getNewTranscoderPath())
    return True
    #raise NotImplementedError("Not yet done please be patient ;)")

def override():
    if os.path.exists(utilsphwrt.getNewTranscoderPath()):
        shutil.copy(utilsphwrt.getNewTranscoderPath(),utilsphwrt.getOriginalTranscoderPath())
        os.chmod(utilsphwrt.getOriginalTranscoderPath(), 0755)
    os.remove(utilsphwrt.getNewTranscoderPath())

    install_phwrt()
    
def local_transcode():
    os.environ["LD_LIBRARY_PATH"] = "%s:$LD_LIBRARY_PATH" % utilsphwrt.getTranscoderPath()
    args = [utilsphwrt.getNewTranscoderPath()] + sys.argv[1:]

     # Spawn the process
    utilsphwrt.log.info("local transcoder with args %s\n" % args)
#todo:
    #if is_debug:
    utilsphwrt.log.info('Debug mode - enabling verbose ffmpeg output')

    # Change logging mode for FFMpeg to be verbose
    for i, arg in enumerate(sys.argv):
        if arg == '-loglevel':
            sys.argv[i+1] = 'verbose'
        elif arg == '-loglevel_plex':
            sys.argv[i+1] = 'verbose'

    proc = subprocess.Popen(args, stderr=subprocess.PIPE)
    while True:
        output = proc.stderr.readline()
        if output == '' and proc.poll() is not None:
            break
        if output:
            utilsphwrt.log.debug(output.strip('\n'))

def transcode(configPath=None):
    utilsphwrt.setup_logging()

    if configPath == None:
        config = utilsphwrt.get_config()
    else:
        config = utilsphwrt.get_config(configPath)
    # Set up the arguments
    #original transcode path args = [getNewTranscoderPath()] + sys.argv[1:]
    old_args = sys.argv[1:]
    # get serveurs list
    servers = config["servers"]

    selected_hostname, selected_host = None, None
    # TODO add loadBalancing # host["port"], host["user"]
    for hostname, host in servers.items():
        selected_hostname= hostname
        selected_host=host

    if selected_host == None or selected_host == None:
        print "can't select server"
        utilsphwrt.log.error("can't select server")
        local_transcode()
        return False
    new_args = utilsphwrt.convertAndFixParameter(config, old_args)
    
    working_dir=""
    if "transcode_path" in config and ( config["transcode_path"]!="" or config["transcode_path"]!=None ):
        working_dir=config["transcode_path"]
    else:
        working_dir=os.getcwd()
    command = REMOTE_ARGS % {
        #"working_dir":  pipes.quote(os.getcwd()),
        "command":      "ffmpeg",
        "args":         ' '.join([pipes.quote(a) for a in new_args])
    }
    utilsphwrt.log.info("Launching transcode_remote with command %s\n" % command)

    if "password" in selected_host and (selected_host["password"]!="" or selected_host["password"]!= None):
        if not find_executable("sshpass"):
            utilsphwrt.log.info("To use ssh with password auth you should install sshpass first")
            local_transcode()
            return False
        new_args = ["sshpass", "-p", "%s" % selected_host["password"],"ssh","-o","UserKnownHostsFile=/dev/null", "-o","StrictHostKeyChecking=no", "-tt", "-R", "32400:127.0.0.1:32400", "%s@%s" % (selected_host["user"], selected_hostname), "-p", selected_host["port"]]
    else:
        if not find_executable("ssh"):
            utilsphwrt.log.info("To use ssh you should install ssh first")
            local_transcode()
            return False
        new_args = ["ssh","-o","UserKnownHostsFile=/dev/null", "-o","StrictHostKeyChecking=no", "-tt", "-R", "32400:127.0.0.1:32400", "%s@%s" % (selected_host["user"], selected_hostname), "-p", selected_host["port"]]

    new_args = new_args + [command]

    utilsphwrt.log.info("Launching transcode_remote with args %s\n" % new_args)

    # Spawn the process
    try:
        proc = subprocess.Popen(new_args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=False)
        proc.wait()
        returnCode = proc.returncode
        result = proc.stdout.readlines()
        if returnCode!=0 or result == []:
            error = proc.stderr.readlines()
            utilsphwrt.log.error("remote transcode failed ! ERROR: %s" % error)
            raise Exception("remote transcode failed ! ERROR: %s" % error)
        else:
            utilsphwrt.log.info(result)
    except:
        utilsphwrt.log.info("switch to local transcoder")
        local_transcode()
        utilsphwrt.log.info(sys.exc_info()[0])

    utilsphwrt.log.info("Transcode stopped on host '%s'" % hostname)

def main():
    # Specific usage options
    if len(sys.argv) < 2 or any((sys.argv[1] == "usage", sys.argv[1] == "help", sys.argv[1] == "-h",
            sys.argv[1] == "?",)):
        usage()
        sys.exit(-1)
    
    if sys.argv[len(sys.argv)-1] == "-d" or sys.argv[len(sys.argv)-1] == "debug":
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

    if sys.argv[1] == "override":
        print "override"
        override()

def usage():
    return ""
