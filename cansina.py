# TODO filter http codes from cmd-opt
# TODO exception management

import requests
import sys
import time
import os
import itertools
import Queue
import threading

from visitador import Visitador
from payload import Payload
from task import Task

THREADS = 4

site = sys.argv[1]
if site[-1] == '/':
    site = site[:-1]

payload = sys.argv[2]

extension = ""
try:
    extension = sys.argv[3]
    print "Using %s extension" % extension
except:
    pass

results = []
banned = []

payload_file = open(payload, 'r')
log_results = open("%s.log" % time.time(), 'w')


def format_result(cad):
    return "{0[2]:^6} {0[1]:^10} {0[0]}{1}".format(cad, os.linesep)

queue = Queue.Queue()
for i in payload_file:
    queue.put(i)
payload_file.close()
total_req = queue.qsize()
current_req = 0
lock = threading.Lock()

if __name__ == '__main__':
    for n in range(0, THREADS):
        print "Starting thread number %s" % n
        v = Visitador(n, queue)
        v.start()
    queue.join()

for res in results:
    log_results.writelines(format_result(res))

log_results.close()
