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
parser.add_argument('-b', dest = 'banned', \
                        help = "banned response codes (default None)", default = ",")
args = parser.parse_args()

target = args.target
payload_filename = args.payload
extension = args.extension
threads = int(args.threads)
banned = [n for n in args.banned.split(',')]
print("Banned extensions: %s" % " ".join(banned))
print("Using %s threads" % threads)

#
# Creating middle objects
#
results = multiprocessing.JoinableQueue()
payload = Payload(target, payload_filename, [extension])
manager = DBManager(urlparse.urlparse(target).netloc.replace(':',''), results, payload.size)
print("Requests: %s / thread" % (payload.size / threads))
#
# Go
#
manager.daemon = True
manager.start()
try:
    for n in range(0, threads):
        v = Visitor(n, payload, results, banned)
        v.daemon = True
        v.start()
    while len(multiprocessing.active_children()) > 1:
        time.sleep(0.1)
    results.join()
    sys.stdout.write('\r')
    sys.stdout.write ("\x1b[0K")
    sys.stdout.flush()
    sys.stdout.write ("Work Done!" + os.linesep)
    sys.stdout.flush()
except Exception as e:
    print(e)