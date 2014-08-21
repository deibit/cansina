#!/usr/bin/env python
import sys
import os
import argparse
import urlparse
import time
import socket

from visitor import Visitor
from payload import Payload
from dbo import DBManager
from inspector import Inspector

USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; es-ES)"


def _check_domain(target_url):
    """Get the target url from the user, clean and return it"""
    domain = urlparse.urlparse(target_url).hostname
    print("Checking " + domain)
    try:
        if socket.gethostbyname(domain):
            pass
    except Exception as ex:
        print("ERROR: Domain doesn't seems to resolve. Check URL")
        print (ex)
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

parser = argparse.ArgumentParser()
parser.add_argument('-u', dest='target',
                    help="target url (ex: http://www.hispasec.com/)",
                    required=True)
parser.add_argument('-p', dest='payload',
                    help="path to the payload file to use",
                    required=True)
parser.add_argument('-e', dest='extension',
                    help="extension list to use ex: php,asp,...(default none)",
                    default="")
parser.add_argument('-t', dest='threads',
                    type=int,
                    help="number of threads (default 4)",
                    default=4)
parser.add_argument('-b', dest='banned',
                    help="banned response codes in format: 404,301,...(default none)",
                    default="404")
parser.add_argument('-a', dest='user_agent',
                    help="the preferred user-agent (default provided)",
                    default=USER_AGENT)
parser.add_argument('-P', dest='proxies',
                    help="set a http and/or https proxy (ex: http://127.0.0.1:8080,https://...",
                    default="")
parser.add_argument('-c', dest='content',
                    help="inspect content looking for a particular string",
                    default="")
parser.add_argument('-d', dest='discriminator',
                    help="if this string if found it will be treated as a 404",
                    default=None)
parser.add_argument('-D', dest='autodiscriminator',
                    help="check for fake 404 (warning: machine decision)",
                    action="store_true",
                    default=False)
parser.add_argument('-U', dest='uppercase',
                    help="MAKE ALL RESOURCE REQUESTS UPPERCASE",
                    action="store_true",
                    default=False)
parser.add_argument('-T', dest='request_delay',
                    help="Time (in milliseconds) between requests",
                    default=False)
parser.add_argument('-A', dest='authentication',
                    help="Basic Authentication (e.g. user:password)",
                    default=False)
parser.add_argument('-H', dest='request_type',
                    help="HTTP HEAD requests",
                    action="store_true")
parser.add_argument('-s', dest='size_discriminator',
                    help="Size (in bytes) for page discriminator",
                    default=False)
parser.add_argument('-S', dest='remove_slash',
                    help="Remove last slash from the requests",
                    default=False,
                    action="store_true")
args = parser.parse_args()

print("")

target = _prepare_target(args.target)

# Processing payload
payload_filename = args.payload

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
        print ("WARNING: HEAD requests make Content inspection useless")

remove_slash = args.remove_slash
if remove_slash:
    print("Requests without last /")

discriminator = args.discriminator
if discriminator:
    print("Discriminator active")
    if request_type == "HEAD":
        print ("WARNING: HEAD requests make Content inspection useless")

autodiscriminator = args.autodiscriminator
autodiscriminator_location = None
if autodiscriminator:
    print("Launching autodiscriminator")
    i = Inspector(target)
    r = i.check_this()
    if r[1] == Inspector.TEST404_URL:
        autodiscriminator_location = r[0]
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

print("Using payload: %s" % payload_filename)
print("Launching %s threads " % threads)


#
# Creating middle objects
#
# - results: queue where visitors will store finished Tasks
#
#   - payload: queue where visitors will get Tasks to do
#
#   - manager: process who is responsible of storing results from results queue
#

payload = Payload(target, payload_filename)
payload.set_extensions(extension)
payload.set_banned_response_codes(banned_response_codes)
payload.set_content(content)
payload.set_remove_slash(remove_slash)
if uppercase:
    payload.set_uppercase()
payload_size = payload.get_length() * len(payload.extensions)
print("Total requests %s  (aprox: %s / thread)" % (payload_size, payload_size / threads))

database_name = urlparse.urlparse(target).hostname
manager = DBManager(database_name)

#
# Starting Manager and Payload processes
#

payload.daemon = True
manager.daemon = True
payload.start()
manager.start()

#try:
Visitor.set_discriminator(discriminator)
Visitor.set_banned_location(autodiscriminator_location)
Visitor.set_user_agent(user_agent)
Visitor.set_proxy(proxy)
Visitor.set_authentication(authentication)
Visitor.set_requests(request_type)
if size_discriminator:
    Visitor.set_size_discriminator(size_discriminator)
if request_delay:
    Visitor.set_delay(request_delay)
thread_pool = []
for number in range(0, threads + 1):
    v = Visitor(number, payload, manager.get_results_queue())
    thread_pool.append(v)
    v.daemon = True
    v.start()

while payload.queue.not_empty:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        print "\nWaiting for threads to stop..."
        manager.dead = True
        payload.flush()
        break

for t in thread_pool:
    t.join()
manager.dead = True
manager.get_results_queue().join()

sys.stdout.write('\r')
sys.stdout.write("\x1b[0K")
time.sleep(0.5)
sys.stdout.write("Work done" + os.linesep)
sys.stdout.flush()

