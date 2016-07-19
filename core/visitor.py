import threading
import time
import sys
import urllib
import os
import hashlib

unuseful_codes = ['404']
strict_codes = ['100', '200', '300', '301', '302', '401', '403', '405', '500']

try:
    import requests
except ImportError:
    print("[CANSINA] Faltal Python module requests not found (install it with pip install requests)")
    sys.exit(1)


class Visitor(threading.Thread):
    auth = None
    user_agent = None
    proxy = None
    discriminator = None
    banned_location = None
    banned_md5 = None
    delay = None
    requests = ""
    size_discriminator = -1
    killed = False


    @staticmethod
    def kill():
        Visitor.killed = True

    @staticmethod
    def set_discriminator(discriminator):
        Visitor.discriminator = discriminator

    @staticmethod
    def set_size_discriminator(size_discriminator):
        Visitor.size_discriminator = int(size_discriminator)

    @staticmethod
    def set_banned_location(banned_location):
        Visitor.banned_location = banned_location

    @staticmethod
    def set_banned_md5(banned_md5):
        Visitor.banned_md5 = banned_md5

    @staticmethod
    def set_user_agent(useragent):
        Visitor.user_agent = useragent

    @staticmethod
    def set_proxy(proxy):
        Visitor.proxy = proxy

    @staticmethod
    def set_delay(delay):
        Visitor.delay = float(delay)

    @staticmethod
    def set_requests(type_request):
        Visitor.requests = type_request

    @staticmethod
    def set_authentication(auth):
        if auth:
            Visitor.auth = tuple(auth.split(':'))
        else:
            Visitor.auth = auth

    def __init__(self, visitor_id, payload, results):
        threading.Thread.__init__(self)
        self.visitor_id = visitor_id
        self.payload = payload
        self.results = results.get_results_queue()

        self.__time = []


    def run(self):
        try:
            while not self.payload.empty():
                if Visitor.killed:
                    break
                self.visit(self.payload.get())
                self.payload.task_done()
        except AttributeError:
            pass
        except Queue.Empty:
            pass


    def visit(self, task):
        try:
            headers = {}
            if Visitor.user_agent:
                headers = {"user-agent": Visitor.user_agent}

            now = time.time()

            if self.__time:
                timeout = sum(self.__time) / len(self.__time)
            else:
                timeout = 10

            r = None
            if Visitor.proxy:
                if Visitor.requests == "GET":
                    r = requests.get(task.get_complete_target(), headers=headers, proxies=Visitor.proxy, verify=False,
                                     timeout=timeout, auth=Visitor.auth)
                elif Visitor.requests == "HEAD":
                    r = requests.head(task.get_complete_target(), headers=headers, proxies=Visitor.proxy, verify=False,
                                      timeout=timeout, auth=Visitor.auth)
            else:
                if Visitor.requests == "GET":
                    r = requests.get(task.get_complete_target(), headers=headers, verify=False, timeout=timeout,
                                     auth=Visitor.auth)
                elif Visitor.requests == "HEAD":
                    r = requests.head(task.get_complete_target(), headers=headers, verify=False, timeout=timeout,
                                      auth=Visitor.auth)

            after = time.time()
            delta = (after - now) * 1000
            tmp_content = r.content
            task.response_size = len(tmp_content)
            task.response_time = delta
            self.__time.append(delta)

            # If discriminator is found we mark it 404
            if Visitor.discriminator and Visitor.discriminator in tmp_content:
                r.status_code = '404'

            #print self.banned_md5 + "  -  " + hashlib.md5("".join(tmp_content)).hexdigest()

            if Visitor.banned_md5 and hashlib.md5("".join(tmp_content)).hexdigest() == self.banned_md5:
                r.status_code = '404'

            # Check if the size of the page is set for discrimante fake 404 errors
            if not Visitor.size_discriminator == 0 and task.response_size == Visitor.size_discriminator:
                r.status_code = '404'
            task.set_response_code(r.status_code)

            # Look for interesting content
            if task.content and (task.content in tmp_content) and not task.response_code == '404':
                task.content_has_detected(True)

            # Look for a redirection
            if r.history and r.history[0]:
                # If redirection is a silly nothing to nothing/ skip it
                if r.url == task.get_complete_target() + '/':
                    pass
                else:
                    # We dont want 404 relocations
                    task.set_location(r.url)
                    if task.location == self.banned_location:
                        task.set_response_code('404')
                    else:
                        task.set_response_code(r.history[0].status_code)
            self.results.put(task)
            if Visitor.delay:
                time.sleep(Visitor.delay)

        except requests.ConnectionError, requests.Timeout:
            sys.stderr.write("Connection (or/and) timeout error" + os.linesep)

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
