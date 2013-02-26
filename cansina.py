import sys
import os
import argparse
import urlparse

from visitor import Visitor
from payload import Payload
from dbo import DBManager

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
payload_filename = args.payload
extension = args.extension
threads = args.threads

#
# Creating middle objects
#
payload = Payload(target, payload_filename, [extension])
manager = DBManager(urlparse.urlparse(target).netloc.replace(':',''))

#
# Go
#
for n in range(0, threads):
    print "Starting thread number %s" % n
    v = Visitor(n, payload, manager)
    v.start()
payload.queue.join()
del manager

