import subprocess
import sys
from utilsphwrt import *

def mount_nfs(configPath=None):
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

    #todo let personalise the remote folder by server
    transcode_path =config["transcode_path"]
    media_path = config["media_path"]
    mkdir = subprocess.Popen("mkdir -p"+transcode_path+"&& mkdir -p "+media_path)
    mkdir.wait()

    mount_transcode = subprocess.Popen("mount -t nfs "+selected_hostname+":"+transcode_path+" "+transcode_path)
    mount_transcode.wait()

    mount_media = subprocess.Popen("mount -t nfs "+selected_hostname+":"+media_path+" "+media_path)
    mount_media.wait()


def main():
    # Specific usage options
    if len(sys.argv) < 2 or any((sys.argv[1] == "usage", sys.argv[1] == "help", sys.argv[1] == "-h",
                                 sys.argv[1] == "?",)):
        usage()
        sys.exit(-1)

    if sys.argv[1] == "mount_nfs":
        print "Mount nfs folder from plex server"
        mount_nfs()

def usage():
    return ""