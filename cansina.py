#!/usr/bin/env python
import sys
import os
import argparse
import urlparse
import time
import socket

from datetime import timedelta

from core.visitor import Visitor
from core.payload import Payload
from core.dbmanager import DBManager
from core.inspector import Inspector
from core.printer import Console

#
#   Default options
#
USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 10.0; Windows NT 9.0; en-EN)"
THREADS = 4
MANAGER_TIMEOUT = 1


#
#   Utility functions
#
def _check_domain(target_url):
    """Get the target url from the user, clean and return it"""

    domain = urlparse.urlparse(target_url).hostname
    print("Resolving " + domain)
    try:
        if socket.gethostbyname(domain):
            pass
    except Exception:
        print("[CANSINA]: Domain doesn't resolve. Check URL")
        sys.exit(1)


def _prepare_target(target_url):
    """Examine target url compliance adding default handle (http://) and look for a final /"""

    if target_url.startswith('http://') or target_url.startswith('https://'):
        pass
    else:
        target_url = 'http://' + target_url
    if target_url.endswith('/') or '***' in target_url:
        pass
    else:
        target_url += '/'
    _check_domain(target_url)
    return target_url


def _prepare_proxies(proxies):
    """It takes a list of proxies and returns a dictionary"""

    if proxies:
        proxies_dict = {}
        for proxy_item in proxies:
            if proxy_item.startswith('http://'):
                proxies_dict['http'] = proxy_item
            elif proxy_item.startswith('https://'):
                proxies_dict['https'] = proxy_item
        return proxies_dict
    return {}

#
# Parsing program options
#
usage = "cansina.py -u url -p payload [options]"
description = '''
Cansina is a web content discovery tool.
It makes requests and analyze the responses trying to figure out whether the
resource is or not accessible.
'''
epilog = "License, requests, etc: https://github.com/deibit/cansina"

parser = argparse.ArgumentParser(usage=usage, description=description, epilog=epilog)
parser.add_argument('-A', dest='authentication', help="Basic Authentication (e.g. user:password)", default=False)
parser.add_argument('-D', dest='autodiscriminator', help="Check for fake 404 (warning: machine decision)", action="store_true", default=False)
parser.add_argument('-H', dest='request_type', help="Make HTTP HEAD requests", action="store_true")
parser.add_argument('-P', dest='proxies', help="Set a http and/or https proxy (ex: http://127.0.0.1:8080,https://...", default="")
parser.add_argument('-S', dest='remove_slash', help="Remove ending slash for payloads", default=False, action="store_true")
parser.add_argument('-T', dest='request_delay', help="Time (a float number, e.g 0.25 or 1.75) between requests", default=0)
parser.add_argument('-U', dest='uppercase', help="Make payload requests uppercase", action="store_true", default=False)
parser.add_argument('-a', dest='user_agent', help="The preferred user-agent (default provided)", default=USER_AGENT)
parser.add_argument('-b', dest='banned', help="List of banned response codes", default="404")
parser.add_argument('-c', dest='content', help="Inspect content looking for a particular string", default="")
parser.add_argument('-d', dest='discriminator', help="If this string if found it will be treated as a 404", default=None)
parser.add_argument('-e', dest='extension', help="Extension list to use ex: php,asp,...(default none)", default="")
parser.add_argument('-p', dest='payload', help="Path to the payload file to use", required=True)
parser.add_argument('-s', dest='size_discriminator', help="Will skip pages with this size in bytes", default=False)
parser.add_argument('-t', dest='threads', type=int, help="Number of threads (default 4)", default=THREADS)
parser.add_argument('-u', dest='target', help="Target url (ex: http://www.hispasec.com/)", required=True)
args = parser.parse_args()

target = _prepare_target(args.target)
extension = args.extension.split(',')
threads = int(args.threads)
banned_response_codes = args.banned.split(',')
user_agent = args.user_agent
proxy = _prepare_proxies(args.proxies.split(','))

request_type = args.request_type
if request_type:
    print("HTTP HEAD requests")
    request_type = "HEAD"
else:
    print("HTTP GET requests")
    request_type = "GET"

content = args.content
if content:
    print("Content inspection selected")
    if request_type == "HEAD":
        print ("WARNING: HEAD request render Content Inspection useless")

remove_slash = args.remove_slash
if remove_slash:
    print("Requests without last /")

discriminator = args.discriminator
if discriminator:
    print("Discriminator active")
    if request_type == "HEAD":
        print ("WARNING: HEAD requests renders Content Inspection useless")

autodiscriminator = args.autodiscriminator
autodiscriminator_location = None
if autodiscriminator:
    print("Launching autodiscriminator")
    i = Inspector(target)
    (result, notfound_type) = i.check_this()
    if notfound_type == Inspector.TEST404_URL:
        autodiscriminator_location = result
        print("404 ---> 302 ----> " + autodiscriminator_location)

print("Banned response codes: %s" % " ".join(banned_response_codes))

if not extension == ['']:
    print("Extensions to probe: %s" % " ".join(extension))

uppercase = args.uppercase
if uppercase:
    print("All resource requests will be done in uppercase")

request_delay = args.request_delay

authentication = args.authentication

size_discriminator = args.size_discriminator

payload_filename = args.payload
print("Using payload: %s" % payload_filename)
print("Spawning %s threads " % threads)
print("Generating payloads...")


#
# Payload queue configuration
#
payload = Payload(target, payload_filename)
payload.set_extensions(extension)
payload.set_remove_slash(remove_slash)
payload.set_uppercase(uppercase)
payload.set_banned_response_codes(banned_response_codes)
payload.set_content(content)

total_requests = payload.get_total_requests()
print("Total requests %s  (aprox: %s / thread)" % (total_requests, total_requests / threads))
payload_queue = payload.get_queue()

#
# Manager queue configuration
#
database_name = urlparse.urlparse(target).hostname
manager = DBManager(database_name)
manager.set_timeout(MANAGER_TIMEOUT)


#
# Configure Visitor Objects
#
Visitor.set_authentication(authentication)
Visitor.set_banned_location(autodiscriminator_location)
Visitor.set_delay(request_delay)
Visitor.set_discriminator(discriminator)
Visitor.set_proxy(proxy)
Visitor.set_requests(request_type)
Visitor.set_size_discriminator(size_discriminator)
Visitor.set_user_agent(user_agent)

#
# Create the thread_pool and start the daemonized threads
#
thread_pool = []
for visitor_id in range(0, threads):
    v = Visitor(visitor_id, payload_queue, manager)
    thread_pool.append(v)
    v.daemon = True
    v.start()

#
#   Run the main thread until manager exhaust all tasks
#
time_before_running = time.time()
Console.header()

while True:
    try:
        if not manager.get_a_task() and any([visitor.is_alive() for visitor in thread_pool]):
            print("Finishing...")
            break
    except KeyboardInterrupt:
        print (os.linesep + "Waiting for threads to stop...")
        Visitor.kill()
        break

time_after_running = time.time()
delta = round(timedelta(seconds=(time_after_running - time_before_running)).total_seconds(), 2)
print("Task took %i seconds" % delta)

sys.stdout.write("\x1b[0K")
sys.stdout.flush()
sys.exit()
