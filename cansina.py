# TODO filter http codes from cmd-opt
# TODO exception management

import requests
import sys
import time
import os
import Queue
import threading
import urlparse
import argparse

from visitor import Visitor
from payload import Payload
from task import Task

#
# Parsing program options
#
parser = argparse.ArgumentParser()
parser.add_argument('-u', dest = 'target', \
                        help = "target url", required = True)
parser.add_argument('-p', dest = 'payload', help = "payload file to use", \
                        required = True)
parser.add_argument('-e', dest = 'extension', \
                        help = "extension to use (default none)", default = "")
parser.add_argument('-t', dest = 'threads', \
                        help = "number of threads (default 4)", default = 4)
args = parser.parse_args()

target = args.target
payload_file = args.payload
extension = args.extension
threads = args.threads

#
# Creating middle objects
#
payload_object = Payload(payload_file, extension)
log_results = open("%s.log" % time.time(), 'w')




def format_result(cad):
    return "{0[2]:^6} {0[1]:^10} {0[0]}{1}".format(cad, os.linesep)

if __name__ == '__main__':
    for n in range(0, THREADS):
        print "Starting thread number %s" % n
        v.start()
    queue.join()

for res in results:
    log_results.writelines(format_result(res))

log_results.close()
