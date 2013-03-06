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
    if not target.startswith('http://') or not target.startswith('https://'):
        target = 'http://' + target
    if not target.endswith('/'):
        target = target + '/'
    _check_domain(target)
    return target

def _prepare_proxies(proxies):
    if proxies:
        proxies_dict = {}
        for proxy in proxies:
            if proxy.startswith('http://'):
                proxies_dict['http'] = proxy
            elif proxy.startswith('https://'):
                proxies_dict['https'] = proxy
        return proxies_dict
    return {}

def _populate_list_with_file(file_name):
    with open(file_name, 'r') as f:
        return f.readlines()

#
# Parsing program options
#

parser = argparse.ArgumentParser()
parser.add_argument('-u', dest = 'target', \
                        help = "target url (ex: http://www.hispasec.com/)", required = True)
parser.add_argument('-p', dest = 'payload', help = "path to the payload file to use", \
                        required = True)
parser.add_argument('-e', dest = 'extension', \
                        help = "extension to use (default none)", default = "")
parser.add_argument('-E', dest = 'extension_filename', \
                        help = "extension file to use (default none)", default = None)
parser.add_argument('-t', dest = 'threads', type=int, \
                        help = "number of threads (default 4)", default = 4)
parser.add_argument('-b', dest = 'banned', \
                        help = "banned response codes in format: 404,301,...(default none)", default = "")
USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; es-ES)"
parser.add_argument('-a', dest = 'user_agent', \
                        help = "the preferred user-agent (default provided)", default = USER_AGENT)
parser.add_argument('-P', dest = 'proxies', \
                        help = "set a http and/or https proxy (ex: http://127.0.0.1:8080,https://...", default = "")
args = parser.parse_args()

target = _prepare_target(args.target)

# Processing payload
payload_filename = args.payload
payload_list = _populate_list_with_file(payload_filename)
payload_list.append(payload_filename)

# Processing extension and extension file
extension_filename = args.extension_filename
extension_list = []
if extension_filename:
    extension_list = _populate_list_with_file(extension_filename)

extension = args.extension
if extension:
    extension_list.insert(0, extension)


threads = int(args.threads)
banned_response_codes = args.banned.split(',')
user_agent = args.user_agent
proxy = _prepare_proxies(args.proxies.split(','))

print("Banned response codes: %s" % " ".join(banned_response_codes))
print("Using payload: %s" % payload_filename)
print("Using %s threads" % threads)
# print("Analizing fake 404...")

#
# Creating middle objects
#
#   - results: queue where visitors will store finished Tasks
#
#   - payload: queue where visitors will get Tasks to do
#
#   - manager: process who is responsible of storing results from results queue
#

results = multiprocessing.JoinableQueue()
payload = Payload(target, payload_list, extension_list, banned_response_codes)
database_name = urlparse.urlparse(target).hostname
manager = DBManager(database_name, results, payload.size)
print("Total requests %s  (%s/thread)" % (payload.size, payload.size / threads))

#
# Go
#

manager.daemon = True
manager.start()
try:
    for n in range(0, threads):
        v = Visitor(n, payload, results, user_agent, proxy)
        v.daemon = True
        v.start()
    while len(multiprocessing.active_children()) > 1:
        time.sleep(0.1)
    results.join()
    sys.stdout.write('\r')
    sys.stdout.write ("\x1b[0K")
    sys.stdout.flush()
    sys.stdout.write ("Work Done!" + os.linesep)
    sys.stdout.flush()
except Exception as e:
    print(e)