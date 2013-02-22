# TODO multithreading
# TODO filter http codes from cmd-opt
# TODO exception management

import requests
import sys
import time
import os
import itertools
import Queue
import threading

THREADS = 4
USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; es-ES)"

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

class Visitador(threading.Thread):
    def __init__(self, id, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.id = id

    def run(self):
        while not self.queue.empty():
            resource = self.queue.get()
            self.visit(resource, extension)
            self.queue.task_done()

    def visit(self, resource, extension):
        try:
            headers = {"user-agent" : USER_AGENT}
            resource = resource.strip()
            sep = "/"
            if len(resource) > 0:
                if resource[0] == '/':
                    sep = ""
            r = requests.get("%s%s%s%s" % (site, sep, resource, extension), headers = headers)
            results.append((site + sep + resource + extension, r.headers['content-length'], r.status_code))
            res = (resource + extension, r.headers['content-length'], r.status_code)
            if not r.status_code in banned:
                sys.stdout.write("(%s) %s" % (self.id, format_result(res)))
        except KeyboardInterrupt:
            sys.exit()
        except requests.ConnectionError, requests.Timeout:
            print "(%s) timeout - sleeping..." % self.id
            time.sleep(5)

if __name__ == '__main__':
    for n in range(0, THREADS):
        print "Starting thread number %s" % n
        v = Visitador(n, queue)
        v.start()
    queue.join()

for res in results:
    log_results.writelines(format_result(res))

payload_file.close()
log_results.close()
