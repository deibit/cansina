#!/usr/bin/env python3
from plugins.inspector import Inspector
from plugins.robots import process_robots
from utils.misc import check_domain, make_cookie_jar, prepare_proxies, prepare_target
from core.resumer import Resumer
from core.printer import Console
from core.dbmanager import DBManager
from core.payload import Payload
from core.visitor import Visitor, strict_codes
import sys
import os
import argparse
import time
import socket
import pickle
import tempfile
import threading
import urllib.parse as urlparse

from datetime import timedelta

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#   Default options
#
USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 10.0; Windows NT 9.0; en-EN)"
THREADS = 4

#
# Parsing program options
#
usage = "cansina.py -u url -p payload [options]"
description = """
Cansina is a web content discovery tool.
It makes requests and analyze the responses trying to figure out whether the
resource is or not accessible.
"""
epilog = "License, requests, etc: https://github.com/deibit/cansina"

parser = argparse.ArgumentParser(usage=usage, description=description, epilog=epilog)
parser.add_argument(
    "-A",
    dest="authentication",
    help="Basic Authentication (e.g: user:password)",
    default=False,
)
parser.add_argument(
    "-C", dest="cookies", help="your cookies (e.g: key:value)", default=""
)
parser.add_argument(
    "-D",
    dest="autodiscriminator",
    help="Check for fake 404 (warning: machine decision)",
    action="store_true",
    default=False,
)
parser.add_argument(
    "-H", dest="request_type", help="Make HTTP HEAD requests", action="store_true"
)
parser.add_argument(
    "-P",
    dest="proxies",
    help="Set a http and/or https proxy (ex: http://127.0.0.1:8080,https://...",
    default="",
)
parser.add_argument(
    "-S",
    dest="remove_slash",
    help="Remove ending slash for payloads",
    default=False,
    action="store_true",
)
parser.add_argument(
    "-T",
    dest="request_delay",
    help="Time (a float number, e.g: 0.25 or 1.75) between requests",
    default=0,
)
parser.add_argument(
    "-U",
    dest="uppercase",
    help="Make payload requests upper-case",
    action="store_true",
    default=False,
)
parser.add_argument(
    "-a",
    dest="user_agent",
    help="The preferred user-agent (default provided)",
    default=USER_AGENT,
)
parser.add_argument(
    "-b", dest="banned", help="List of banned response codes", default="404"
)
parser.add_argument(
    "-B",
    dest="unbanned",
    help="List of unbanned response codes, mark all response as invalid without unbanned response codes, higher priority than banned",
    default="",
)
parser.add_argument(
    "-c",
    dest="content",
    help="Inspect content looking for a particular string",
    default="",
)
parser.add_argument(
    "-d",
    dest="discriminator",
    help="If this string if found it will be treated as a 404",
    default=None,
)
parser.add_argument(
    "-e",
    dest="extension",
    help="Extension list to use e.g: php,asp,...(default none)",
    default="",
)

parser.add_argument(
    "-o",
    dest="output",
    help="Write (append) results in CSV format to a file; -o <filename>",
    default="",
)

parser.add_argument(
    "-p",
    dest="payload",
    help="A single file, a file with filenames (.payload) or a directory (will do *.txt)",
    default=None,
)
parser.add_argument(
    "-s",
    dest="size_discriminator",
    help="Will skip pages with this size in bytes (or a list of sizes 0,500,1500...)",
    default=False,
)
parser.add_argument(
    "-t",
    dest="threads",
    type=int,
    help="Number of threads (default 4)",
    default=THREADS,
)
parser.add_argument("-u", dest="target", help="Target url", default=None)
parser.add_argument("-r", dest="resume", help="Resume a session", default=False)
parser.add_argument(
    "-R",
    dest="parse_robots",
    action="store_true",
    help="Parse robots.txt and check its contents",
    default=False,
)
parser.add_argument(
    "--recursive",
    dest="recursive",
    help="Recursive descend on path directories",
    default=False,
    action="store_true",
)
parser.add_argument(
    "--no-persist",
    dest="persist",
    help="Do not Use HTTP persistent connections",
    default=True,
    action="store_false",
)
parser.add_argument(
    "--full-path",
    dest="full_path",
    help="Show full path instead of only resources",
    default=False,
    action="store_true",
)
parser.add_argument(
    "--show-type",
    dest="show_content_type",
    help="Show content-type in results",
    default=False,
    action="store_true",
)
parser.add_argument(
    "--no-follow",
    dest="allow_redirects",
    help="Do not follow redirections",
    default=True,
    action="store_false",
)
parser.add_argument(
    "--line",
    dest="continue_line",
    type=int,
    help="Continue payload in line <n>",
    default=0,
)

parser.add_argument(
    "--resumer",
    dest="do_resumer",
    help="Save session in a file",
    default=False,
    action="store_true",
)

parser.add_argument(
    "--headers",
    dest="headers",
    help="Set personalized headers: key=value;key=value...",
    default="",
)
parser.add_argument(
    "--capitalize",
    dest="capitalize",
    help="Transform 'word' into 'Word'.",
    default=False,
    action="store_true",
)
parser.add_argument(
    "--strip-extension",
    dest="strip_extension",
    help="Strip word extension: word.ext into word",
    default=False,
    action="store_true",
)
parser.add_argument(
    "--alpha",
    dest="only_alpha",
    help="Filter non alphanumeric words from wordlist",
    default=False,
    action="store_true",
)
parser.add_argument(
    "--no-progress",
    dest="no_progress",
    help="Don't show tested words and progress. (For dumb terminals)",
    default=False,
    action="store_true",
)
parser.add_argument(
    "--no-colors",
    dest="no_colors",
    help="Don't use output colors to keep output clean, e.g. when redirecting output to file",
    default=False,
    action="store_true",
)

args = parser.parse_args()

# Initialize a Resumer object
resumer = Resumer(args, args.continue_line)
resume = args.resume
# If we are ressuming a former session revive last args object
if resume:
    try:
        with open(resume, "rb") as f:
            resumer = pickle.load(f)
            args = resumer.get_args()
    except:
        sys.stdout.write("[!] Could not load a correct resume file, sorry.")
        sys.exit()

# Target check and preparation
if not args.target:
    print("[!] You need to specify a target")
    parser.print_help()
    sys.exit()
target = prepare_target(args.target)

Console.add_config("{:37} {:>}".format("Target:", target))

recursive = args.recursive
Console.add_config(
    "{:37} {:>}".format("Recursive requests", "Yes" if recursive else "No")
)

# Persistent connections
persist = args.persist
Console.add_config(
    "{:37} {:>}".format("Persistent connections", "Yes" if persist else "No")
)


# Misc options
extension = args.extension.split(",")
threads = int(args.threads)
banned_response_codes = [int(item) for item in args.banned.split(",") if item]
unbanned_response_codes = [
    int(item)
    for item in args.unbanned.split(",")
    if item and item not in banned_response_codes
]
user_agent = args.user_agent
proxy = prepare_proxies(args.proxies.split(","))
cookies = args.cookies
request_delay = args.request_delay
authentication = args.authentication
size_discriminator = args.size_discriminator
output = args.output

# Personalized headers
personalized_headers = {}
try:
    if args.headers:
        for header in args.headers.split(","):
            k, v = header.split("=")
            personalized_headers[k] = v
except Exception as e:
    print("[?] Check personalized headers format: header=value,header=value...")
    sys.exit()

# HEAD / GET requests
request_type = args.request_type
if request_type:
    request_type = "HEAD"
else:
    request_type = "GET"

Console.add_config("{:37} {:>}".format("Requests type:", request_type))

# Content inspecting
content = args.content

# Remove slash (probably an ancient option)
remove_slash = args.remove_slash

# Discriminator option
discriminator = args.discriminator

# Autodiscriminator (probably deprecated by future diagnostic subsystem)
autodiscriminator = args.autodiscriminator
autodiscriminator_location = None
autodiscriminator_md5 = None
if autodiscriminator:
    i = Inspector(target)
    (result, notfound_type) = i.check_this()
    if notfound_type == Inspector.TEST404_URL:
        autodiscriminator_location = result
    elif notfound_type == Inspector.TEST404_MD5:
        autodiscriminator_md5 = result

# Misc user information


Console.add_config(
    "{:37} {:>}".format(
        "Filtered response codes:",
        ",".join([str(item) for item in banned_response_codes]),
    )
)


unbanned_response_codes = (
    unbanned_response_codes if unbanned_response_codes else strict_codes
)
unbanned_codes = [str(i) for i in unbanned_response_codes]
Console.add_config("{:37} {:>}".format("Ok response codes:", ",".join(unbanned_codes)))

# Using Custom File Extension List
Console.add_config(
    "{:37} {:>}".format(
        "Custom extensions:", ",".join(extension) if not extension == [""] else "No"
    )
)

# Payload options
# FIXME: This design is garbage
payload = None
parse_robots = args.parse_robots
remove_slash = True
if parse_robots:
    robots_content = process_robots(target)
    if not robots_content:
        print("[!] robots.txt not found")
        sys.exit()
    payload_filename = robots_content
else:
    payload_filename = args.payload
    if not payload_filename:
        print("[!] You have to specify a payload")
        parser.print_help()
        sys.exit()

Console.add_config("{:37} {:>}".format("Payload:", payload_filename))
payload = Payload(target, payload_filename, resumer)

# Uppercase
if args.uppercase:
    payload.set_uppercase()

# Capitalization
if args.capitalize:
    payload.set_capitalize()

# Strip extension
if args.strip_extension:
    payload.set_strip_extension()

# Only alphanumeric words
if args.only_alpha:
    payload.set_alpha()

#
# Payload queue configuration
#
payload.set_extensions(extension)
payload.set_remove_slash(remove_slash)
payload.set_banned_response_codes(banned_response_codes)
payload.set_unbanned_response_codes(unbanned_response_codes)
payload.set_content(content)
payload.set_recursive(recursive)

payload_queue = payload.get_queue()
total_requests = payload.get_total_requests()

#
# Manager queue configuration
#
database_name = (
    urlparse.urlparse(target).scheme + "_" + urlparse.urlparse(target).hostname
)
if urlparse.urlparse(target).port is not None:
    database_name += "_" + str(urlparse.urlparse(target).port)
manager = DBManager(database_name)
manager.output = output
manager_lock = threading.Lock()

#
# Configure Visitor Objects
#
Visitor.set_authentication(authentication)
Visitor.set_banned_location(autodiscriminator_location)
Visitor.set_banned_md5(autodiscriminator_md5)
Visitor.set_delay(request_delay)
Visitor.set_discriminator(discriminator)
Visitor.set_proxy(proxy)
Visitor.set_requests(request_type)
Visitor.set_size_discriminator(size_discriminator)
Visitor.set_user_agent(user_agent)
Visitor.set_persist(persist)
Visitor.allow_redirects(args.allow_redirects)
Visitor.set_headers(personalized_headers)

# Cookies
try:
    cookie_jar = make_cookie_jar(cookies)
    Visitor.set_cookies(cookie_jar)
except:
    print("[!] Error setting cookies. Review cookie string (key:value,key:value...)")
    sys.exit()

# Select if full path is prefered
full_path = args.full_path

# Select if user wants content-type print
show_content_type = args.show_content_type

#
#   Run the main thread until manager exhaust all tasks
#
time_before_running = time.time()
Console.number_of_requests = payload.get_total_requests()
Console.number_of_threads = threads
Console.show_full_path = full_path
Console.show_content_type = show_content_type
Console.set_show_progress(False if args.no_progress else True)
Console.set_show_colors(False if args.no_colors else True)
Console.init()

#
# Create the thread_pool and start the daemonized threads
#
thread_pool = []
for visitor_id in range(threads):
    v = Visitor(visitor_id, payload_queue, manager, manager_lock)
    thread_pool.append(v)
    v.start()

# Main loop
try:
    payload_queue.join()

    for thread in thread_pool:
        payload_queue.put(None)
    for visitor in thread_pool:
        visitor.join()

except KeyboardInterrupt:
    Console.say("Waiting for threads to stop...")

    Visitor.kill()

    for visitor in thread_pool:
        visitor.join()

    if args.do_resumer:
        resumer.set_line(payload_queue.get().get_number())
        with open(
            "resume_file_" + time.strftime("%d_%m_%y_%H_%M", time.localtime()), "wb"
        ) as f:
            pickle.dump(resumer, f)

except Exception as e:
    import traceback as tb

    Console.say(tb.print_tb(sys.exc_info()[2]))

finally:
    # Dump results to database
    manager.save()
    Console.end()

sys.exit()
