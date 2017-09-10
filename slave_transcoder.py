import sys

def mount_nfs():


def main():
    # Specific usage options
    if len(sys.argv) < 2 or any((sys.argv[1] == "usage", sys.argv[1] == "help", sys.argv[1] == "-h",
                                 sys.argv[1] == "?",)):
        usage()
        sys.exit(-1)

    if sys.argv[1] == "mount_nfs":
        print "Mount nfs folder from plex server"
        install_phwrt()