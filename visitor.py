import multiprocessing
import requests
import time
import sys

SLEEP_TIME = 3

class Visitor(multiprocessing.Process):
    def __init__(self, id, payload, results, banned, user_agent):
        multiprocessing.Process.__init__(self)
        self.id = id
        self.payload = payload
        self.results = results
        self.banned = banned
        self.user_agent = user_agent

    def run(self):
        while not self.payload.queue.empty():
            self.visit(self.payload.queue.get())
            self.payload.queue.task_done()

    def visit(self, task):
        try:
            headers = {"user-agent" : self.user_agent}
            now = time.time()
            r = requests.get(task.get_complete_target())
            after = time.time()
            delta = (after - now) * 1000
            task.response_code = r.status_code
            task.response_size = len(r.content)
            task.response_time = delta
            self.results.put(task)
            if str(task.response_code) in self.banned:
                task.valid = False

        except requests.ConnectionError, requests.Timeout:
            sys.stdout.write("(%s) timeout - sleeping...\n" % self.id)
            time.sleep(SLEEP_TIME)

    def terminate(self):
        print "process %s terminated" % self.pid
        multiprocessing.Process.terminate(self)
