import sys
import os
import argparse
import urlparse
import Queue
import time
import multiprocessing

from visitor import Visitor
from payload import Payload
from dbo import DBManager
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
parser.add_argument('-t', dest = 'threads', type=int, \
                        help = "number of threads (default 4)", default = 4)
args = parser.parse_args()

target = args.target
payload_filename = args.payload
extension = args.extension
threads = int(args.threads)

#
# Creating middle objects
#
results = multiprocessing.JoinableQueue()
payload = Payload(target, payload_filename, [extension])
manager = DBManager(urlparse.urlparse(target).netloc.replace(':',''), results)

#
# Go
#
manager.daemon = True
manager.start()
try:
    for n in range(0, threads):
        print "Starting thread number %s" % n
        v = Visitor(n, payload, results)
        v.daemon = True
        v.start()
    while len(multiprocessing.active_children()) > 1:
        time.sleep(0.1)
    results.join()
except Exception as e:
    print(e)