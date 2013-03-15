#!/usr/bin/env python
import sys
import os
import argparse
import urlparse
import time
import multiprocessing
import socket

from visitor import Visitor
from payload import Payload
from dbo import DBManager
from inspector import Inspector

def _check_domain(target):
    '''Get the target url from the user, clean and return it'''
    domain = urlparse.urlparse(target).hostname
    print("Checking " + domain)
    try:
        if socket.gethostbyname(domain):
            pass
    except Exception as e:
        print("ERROR: Domain doesn't seems to resolve. Check URL")
        sys.exit(1)

def _prepare_target(target):
    '''Examine target url compliance adding default handle (http://) and look for a final /'''
    if target.startswith('http://') or target.startswith('https://'):
        pass
    else:
        target = 'http://' + target
    if not target.endswith('/'):
        target = target + '/'
    _check_domain(target)
    return target

def _prepare_proxies(proxies):
    '''It takes a list of proxies and returns a dictionary'''
    if proxies:
        proxies_dict = {}
        for proxy in proxies:
            if proxy.startswith('http://'):
                proxies_dict['http'] = proxy
            elif proxy.startswith('https://'):
                proxies_dict['https'] = proxy
        return proxies_dict
    return {}

#
# Parsing program options
#

parser = argparse.ArgumentParser()
parser.add_argument('-u', dest = 'target',
                    help = "target url (ex: http://www.hispasec.com/)",
                    required = True)
parser.add_argument('-p', dest = 'payload',
                    help = "path to the payload file to use",
                    required = True)
parser.add_argument('-e', dest = 'extension',
                    help = "extension list to use ex: php,asp,...(default none)",
                    default = "")
parser.add_argument('-t', dest = 'threads',
                    type=int,
                    help = "number of threads (default 4)",
                    default = 4)
parser.add_argument('-b', dest = 'banned',
                    help = "banned response codes in format: 404,301,...(default none)",
                    default = "404")
USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; es-ES)"
parser.add_argument('-a', dest = 'user_agent',
                    help = "the preferred user-agent (default provided)",
                    default = USER_AGENT)
parser.add_argument('-P', dest = 'proxies',
                    help = "set a http and/or https proxy (ex: http://127.0.0.1:8080,https://...",
                    default="")
parser.add_argument('-c', dest = 'content',
                    help = "inspect content looking for a particular string",
                    default = "")
parser.add_argument('-d', dest = 'discriminator',
                    help = "if this string if found it will be treated as a 404",
                    default = None)
parser.add_argument('-D', dest = 'autodiscriminator',
                    help = "check for fake 404 (warning: machine decision)",
                    action="store_true",
                    default=False)
parser.add_argument('-U', dest = 'uppercase',
                    help = "MAKE ALL RESOURCE REQUESTS UPPERCASE",
                    action="store_true",
                    default=False)
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

content = args.content
if content:
    print("Content inspection selected")

discriminator = args.discriminator
if discriminator:
    print("Discriminator active")

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

print("Using payload: %s" % payload_filename)
print("Using %s threads " % threads)

#
# Creating middle objects
#
#   - results: queue where visitors will store finished Tasks
#
#   - payload: queue where visitors will get Tasks to do
#
#   - manager: process who is responsible of storing results from results queue
#

payload = Payload(target, payload_filename)
payload.set_extensions(extension)
payload.set_banned_response_codes(banned_response_codes)
payload.set_content(content)
if uppercase:
    payload.set_uppercase()
payload_size = payload.get_length() * len(extension)
print("Total requests %s  (%s / thread)" % (payload.get_length(), payload.get_length() / threads))

database_name = urlparse.urlparse(target).hostname
manager = DBManager(database_name)

#
# Starting Manager and Payload processes
#

payload.daemon = True
manager.daemon = True
payload.start()
manager.start()
# Give payload and manager time to get ready
time.sleep(1)

try:
    if discriminator:
        Visitor.set_discriminator(discriminator)
    Visitor.set_banned_location(autodiscriminator_location)
    Visitor.set_user_agent(user_agent)
    Visitor.set_proxy(proxy)
    for number in range(0, threads):
        v = Visitor(number, payload, manager.get_results_queue())
        v.daemon = True
        v.start()

    while len(multiprocessing.active_children()) > 1:
        time.sleep(0.1)
    manager.get_results_queue().join()

    sys.stdout.write('\r')
    sys.stdout.write ("\x1b[0K")
    sys.stdout.flush()
    time.sleep(0.5)
    sys.stdout.write("Work Done!" + os.linesep)
    sys.stdout.flush()

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print("cansina.py", exc_type, fname, exc_tb.tb_lineno)
