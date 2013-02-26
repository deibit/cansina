import threading
import requests
import time

from task import Task

USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; es-ES)"

class Visitor(threading.Thread):

    def __init__(self, id, payload, dbmanager):
        threading.Thread.__init__(self)
        self.id = id
        self.payload = payload
        self.dbmanager = dbmanager

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
            self.dbmanager.queue.put(task)
            task.print_report()

        except KeyboardInterrupt:
            sys.exit()
        except requests.ConnectionError, requests.Timeout:
            print "(%s) timeout - sleeping..." % self.id
            time.sleep(5)
