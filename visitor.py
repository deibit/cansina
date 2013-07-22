import multiprocessing
import time
import sys
import urllib

try:
    import requests
except:
    print("Python module requests not found")
    sys.exit(1)

SLEEP_TIME = 3

class Visitor(multiprocessing.Process):

    user_agent = None
    proxy = None
    discriminator = None
    banned_location = None
    delay = 0

    @staticmethod
    def set_discriminator(discriminator):
        Visitor.discriminator = discriminator

    @staticmethod
    def set_banned_location(banned_location):
        Visitor.banned_location = banned_location

    @staticmethod
    def set_user_agent(useragent):
        Visitor.user_agent = useragent

    @staticmethod
    def set_proxy(proxy):
        Visitor.proxy = proxy

    @staticmethod
    def set_delay(delay):
        Visitor.delay = int(delay)

    @staticmethod
    def set_authentication(auth):
        Visitor.auth = tuple(auth.split(':'))

    def __init__(self, number, payload, results):
        multiprocessing.Process.__init__(self)
        self.number = number
        self.payload = payload
        self.results = results

        self.__time = []

    def run(self):
        while not self.payload.queue.empty():
            self.visit(self.payload.queue.get())
            self.payload.queue.task_done()

    def visit(self, task):
        try:
            headers = {}
            if Visitor.user_agent:
                headers = {"user-agent" : Visitor.user_agent}

            now = time.time()

            if self.__time:
                timeout = sum(self.__time) / len(self.__time)
            else:
                timeout = 10

            r = None
            if Visitor.proxy:
                r = requests.get(task.get_complete_target(), headers=headers, proxies=Visitor.proxy, verify=False, timeout=timeout, auth=Visitor.auth)
            else:
                r = requests.get(task.get_complete_target(), headers=headers, verify=False, timeout=timeout, auth=Visitor.auth)
            after = time.time()
            delta = (after - now) * 1000
            tmp_content = r.content
            task.response_size = len(tmp_content)
            task.response_time = delta
            self.__time.append(delta)

            # If discriminator is found we mark it 404
            if Visitor.discriminator and Visitor.discriminator in tmp_content:
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
                    task.set_location(r.url)
                    if task.location == self.banned_location:
                        task.set_response_code('404')
                    else:
                        task.set_response_code(r.history[0].status_code)
            self.results.put(task)
            if self.delay:
                time.sleep(float(Visitor.delay / 0.001))

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
