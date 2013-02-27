import sys
import os
import argparse
import urlparse
import Queue
import time

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
queue = Queue.Queue()
payload = Payload(target, payload_filename, [extension])
manager = DBManager(urlparse.urlparse(target).netloc.replace(':',''), queue)

#
# Go
#
manager.start()
try:
    for n in range(0, threads):
        print "Starting thread number %s" % n
        v = Visitor(n, payload, queue)
        v.daemon = True
        v.start()
    while not payload.queue.empty():
        time.sleep(0.1)
    # payload.queue.join()
#     queue.put(Task("STOP", "STOP", "STOP"))
#     queue.join()
# except:
#     pass

except KeyboardInterrupt:
    sys.stdout.write("Quitting by user...shutting down")
    payload.queue.
    sys.exit(1)

finally:
    queue.put(Task("STOP", "STOP", "STOP"))
    queue.join()

