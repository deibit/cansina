#!/usr/bin/env python
import sys
import sqlite3
import argparse
import urlparse


RED = '\033[31m'
MAGENTA = '\033[35m'
BLUE = '\033[34m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
LBLUE = '\033[36m'
ENDC = '\033[0m'

colors = {'200': GREEN,
          '302': BLUE,
          '403': RED,
          '500': YELLOW}


parser = argparse.ArgumentParser()
parser.add_argument('-p',
                    dest='project_name',
                    help='path to sqlite project database',
                    required=True)

parser.add_argument('-c',
                    dest='response_codes',
                    help='comma separate list of http codes responses to print',
                    required=False)

parser.add_argument('-u',
                    help='list used payload on visited resources',
                    action='store_true')

args = parser.parse_args()

project_name = args.project_name
response_codes = args.response_codes
used_payloads = args.u

if not response_codes:
    response_codes = ['200', '302', '403']

QUERY = "SELECT * FROM requests ORDER BY resource"
if used_payloads:
        QUERY = "SELECT url,payload FROM requests ORDER BY url"

try:
    with sqlite3.connect(project_name) as connection:
        cursor = connection.cursor()
        cursor.execute(QUERY)
        data = cursor.fetchall()

except Exception, e:
    print("Error opening database {}".format(project_name))
    print("Details: {}".format(e))
    sys.exit(-1)


def comparator(a, b):
    if a.count('/') < b.count('/'):
        return -1
    if a.count('/') > b.count('/'):
        return 1
    if a.count('/') == b.count('/'):
        return 0

if used_payloads:
    output = {}
    for k, v in data:
        if not output.has_key(k):
            output[k] = [v]
            continue
        output[k].append(v)
    for k in output.keys():
        print ("{}{}:".format(GREEN,k))
        output[k].sort()
        for v in set(output[k]):
            print ("        {}{}".format(BLUE,v))
    sys.exit()

data.sort(cmp=comparator, key=lambda x: x[2] + x[3] + x[4])
for line in data:
    (url, resource, extension, response_code, location, response_size) = \
        line[2], line[3], line[4], line[5], line[8], line[6]
    if response_code in response_codes:
        url = urlparse.urlparse(url)
        if not location:
            print("{}{} {:>8}: {}{}{}".format(colors[response_code],
                                              response_code, response_size,
                                              url.path, resource, extension))
        else:
            print("{}{} {:>8}: {}{}{} -> {}".format(colors[response_code],
                                                    response_code,
                                                    response_size, url.path,
                                                    resource, extension,
                                                    location))
