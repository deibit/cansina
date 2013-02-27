import threading
import requests
import time
import sys

from task import Task

USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; es-ES)"
SLEEP_TIME = 3

class Visitor(threading.Thread):

    def __init__(self, id, payload, queue):
        threading.Thread.__init__(self)
        self.id = id
        self.payload = payload
        self.queue = queue

    def run(self):
        while not self.payload.queue.empty():
            self.visit(self.payload.queue.get())
            self.payload.queue.task_done()

    def visit(self, task):
        try:
            headers = {"user-agent" : USER_AGENT}
            now = time.time()
            r = requests.get(task.get_complete_target())
            after = time.time()
            delta = after - now
            task.response_code = r.status_code
            task.response_size = len(r.content)
            task.response_time = delta
            self.queue.put(task)
            task.print_report()

        except requests.ConnectionError, requests.Timeout:
            sys.stdout.write("(%s) timeout - sleeping..." % self.id)
            time.sleep(SLEEP_TIME)
