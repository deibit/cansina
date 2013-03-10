import multiprocessing
import time
import sys
import urllib

try:
    import requests
except:
    print("Python module requests not found")
    sys.exit(1)

from task import Task

SLEEP_TIME = 3

class Visitor(multiprocessing.Process):
    def __init__(self, number, payload, results, user_agent, proxy, discriminator, banned_location):
        multiprocessing.Process.__init__(self)
        self.number = number
        self.payload = payload
        self.results = results
        self.user_agent = user_agent
        self.proxy = proxy
        self.discriminator = discriminator
        self.banned_location = banned_location

    def run(self):
        while not self.payload.queue.empty():
            self.visit(self.payload.queue.get())
            self.payload.queue.task_done()

    def visit(self, task):
        try:
            headers = {"user-agent" : self.user_agent}

            now = time.time()

            r = None
            if self.proxy:
                r = requests.get(task.get_complete_target(), headers=headers, proxies=self.proxy)
            else:
                r = requests.get(task.get_complete_target(), headers=headers)
            after = time.time()
            delta = (after - now) * 1000
            tmp_content = r.content
            task.response_size = len(tmp_content)
            task.response_time = delta

            # If discriminator is found we mark it 404
            if self.discriminator and self.discriminator in tmp_content:
                r.status_code = '404'

            task.set_response_code(r.status_code)

            # Look for interesting content
            if task.content and (task.content in tmp_content) and not task.response_code == '404':
                task.content_has_detected(True)

            # Look for a redirection
            if r.history and r.history[0]:
                if r.url == task.get_complete_target() + '/':
                    pass
                else:
                    # We dont want those pesky 404 relocations
                    task.location = r.url
                    if task.location == self.banned_location:
                        task.set_response_code('404')
                    else:
                        task.set_response_code(r.history[0].status_code)
            self.results.put(task)

        except requests.ConnectionError, requests.Timeout:
            sys.stdout.write("(%s) timeout - sleeping...\n" % self.number)
            time.sleep(SLEEP_TIME)

        except ValueError:
            # Falling back to urllib (requests doesnt want freak chars)
            now = time.time()
            r = urllib.urlopen(task.get_complete_target(), proxies=self.proxy)
            after = time.time()
            delta = (after - now) * 1000
            task.set_response_code(r.code)
            c = r.readlines()
            task.response_time = delta
            task.response_size = len(c)
            self.results.put(task)

        except Exception as e:
            print e.args

    def terminate(self):
        print "process %s terminated" % self.pid
        multiprocessing.Process.terminate(self)
