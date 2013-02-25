import threading
import requests

USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; es-ES)"

class Visitor(threading.Thread):

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
            lock.acquire()
            current_req = current_req + 1
            lock.release()
            results.append((site + sep + resource + extension, r.headers['content-length'], r.status_code))
            res = (resource + extension, r.headers['content-length'], r.status_code)
            if not r.status_code in banned:
                sys.stdout.write("(%s) [%s/%s] %s" % (self.id, current_req, total_req, format_result(res)))
        except KeyboardInterrupt:
            sys.exit()
        except requests.ConnectionError, requests.Timeout:
            print "(%s) timeout - sleeping..." % self.id
            time.sleep(5)
