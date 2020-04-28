import threading
import time
import sys
import urllib
import hashlib
import requests


unuseful_codes = [404]
strict_codes = [100, 200, 300, 301, 302, 401, 403, 405, 500]


class Visitor(threading.Thread):
    auth = None
    banned_location = None
    banned_md5 = None
    cookies = None
    delay = None
    discriminator = None
    headers = {}
    is_allow_redirects = False
    persist = False
    proxy = None
    requests = ""
    size_discriminator = []
    user_agent = None
    killed = False

    @staticmethod
    def set_headers(headers):
        Visitor.headers = headers

    @staticmethod
    def allow_redirects(pref):
        Visitor.is_allow_redirects = pref

    @staticmethod
    def set_discriminator(discriminator):
        Visitor.discriminator = discriminator

    @staticmethod
    def set_cookies(_cookies):
        Visitor.cookies = _cookies

    @staticmethod
    def kill():
        Visitor.killed = True

    @staticmethod
    def set_size_discriminator(size_discriminator):
        if size_discriminator:
            Visitor.size_discriminator = [int(x) for x in size_discriminator.split(",")]
        else:
            Visitor.size_discriminator = []

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
        Visitor.auth = tuple(auth.split(":")) if auth else auth

    @staticmethod
    def set_persist(persist):
        Visitor.persist = persist

    def __init__(self, visitor_id, payload, results, lock):
        threading.Thread.__init__(self)
        self.visitor_id = visitor_id
        self.payload = payload
        self.results = results
        self.session = None
        self.lock = lock

    def run(self):
        try:
            while not Visitor.killed:
                task = self.payload.get()
                if task == None:
                    return
                self.visit(task)
                self.payload.task_done()
        except:
            pass

    def visit(self, task):
        def _dumb_redirect(url):
            origin = "{0}{1}".format(task.target, task.resource)

            # Detect redirect to same page but ended with slash
            if url == origin:
                return True
            if url == origin + "/":
                return True

            # Detect redirect to root
            if url == task.target:
                return True

            return False

        try:
            if Visitor.user_agent:
                Visitor.headers["User-Agent"] = Visitor.user_agent

            # Persistent connections
            if Visitor.persist:
                if not self.session:
                    self.session = requests.Session()
            else:
                self.session = requests

            r = None
            if Visitor.proxy:
                if Visitor.requests == "GET":
                    r = self.session.get(
                        task.get_complete_target(),
                        headers=Visitor.headers,
                        proxies=Visitor.proxy,
                        verify=False,
                        auth=Visitor.auth,
                        cookies=Visitor.cookies,
                        allow_redirects=Visitor.is_allow_redirects,
                    )

                elif Visitor.requests == "HEAD":
                    r = self.session.head(
                        task.get_complete_target(),
                        headers=Visitor.headers,
                        proxies=Visitor.proxy,
                        verify=False,
                        auth=Visitor.auth,
                        cookies=Visitor.cookies,
                        allow_redirects=Visitor.is_allow_redirects,
                    )
            else:
                if Visitor.requests == "GET":
                    r = self.session.get(
                        task.get_complete_target(),
                        headers=Visitor.headers,
                        verify=False,
                        auth=Visitor.auth,
                        cookies=Visitor.cookies,
                        allow_redirects=Visitor.is_allow_redirects,
                    )

                elif Visitor.requests == "HEAD":
                    r = self.session.head(
                        task.get_complete_target(),
                        headers=Visitor.headers,
                        verify=False,
                        auth=Visitor.auth,
                        cookies=Visitor.cookies,
                        allow_redirects=Visitor.is_allow_redirects,
                    )

            tmp_content = r.content
            task.response_size = len(tmp_content)
            task.response_time = round(r.elapsed.microseconds / 1000, 2)

            task.set_response_code(r.status_code)

            # If discriminator is found we mark it 404
            if sys.version_info[0] >= 3:
                tmp_content = tmp_content.decode("Latin-1")
            if Visitor.discriminator and Visitor.discriminator in tmp_content:
                task.ignorable = True

            if (
                Visitor.banned_md5
                and hashlib.md5("".join(tmp_content)).hexdigest() == self.banned_md5
            ):
                task.ignorable = True

            # Check if page size is not what we need
            if task.response_size in Visitor.size_discriminator:
                task.ignorable = True

            # Look for interesting content
            if task.content and (task.content in tmp_content):
                task.content_has_detected(True)

            # Look for a redirection
            if Visitor.is_allow_redirects:
                if len(r.history) > 0 and not _dumb_redirect(r.history[-1].url):
                    task.response_code = str(r.history[0].status_code)
                    task.location = r.history[-1].url
            else:
                if r.status_code >= 300 and r.status_code < 400:
                    task.set_response_code(404)
                    task.ignorable = True

            if "content-type" in [h.lower() for h in r.headers.keys()]:
                try:
                    task.response_type = r.headers["Content-Type"].split(";")[0]
                except:
                    pass

            task.thread = self.visitor_id
            self.lock.acquire()
            self.results.put(task)

            if Visitor.delay:
                time.sleep(Visitor.delay)

        except (requests.ConnectionError, requests.Timeout) as e:
            # TODO log to a file instead of screen
            print("[!] Timeout/Connection error")
            print(e)
            pass

        except Exception as e:
            print("[!] General exception while visiting")
            print(e)
            pass

        finally:
            self.lock.release()
            return
