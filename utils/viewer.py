#!/usr/bin/env python
import sys
import sqlite3
import argparse

try:
    from asciitree import LeftAligned
except:
    print("install asciitree for -t option")

try:
    import urlparse
except:
    import urllib.parse as urlparse

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
                    help='list the payload used on visited resources',
                    action='store_true')

parser.add_argument('-t',
                    dest='tree',
                    help='print a tree with the discoreved structure',
                    required=False,
                    action='store_true')

parser.add_argument('-e',
                    dest='banned_extensions',
                    help='comma separate list of extensions you do not want to see',
                    required=False)

parser.add_argument('-E',
                    dest='unbanned_extensions',
                    help='comma separate list of the extensions you only want to see (will include directories)',
                    required=False)

parser.add_argument('-s',
                    dest='size_filter',
                    help='comma separate list of size files you do not want to see',
                    required=False)


args = parser.parse_args()

project_name = args.project_name
response_codes = args.response_codes
banned_extensions = args.banned_extensions
unbanned_extensions = args.unbanned_extensions
size_filter = args.size_filter
used_payloads = args.u
tree = args.tree

if not response_codes:
    response_codes = ['200', '302', '403']

QUERY = "SELECT * FROM requests ORDER BY resource"
if used_payloads:
        QUERY = "SELECT url,payload FROM requests ORDER BY url"

try:
    with sqlite3.connect(project_name) as connection:
        cursor = connection.cursor()
        connection.text_factory = str
        cursor.execute(QUERY)
        data = cursor.fetchall()

except Exception as e:
    print("Error opening database {}".format(project_name))
    print("Details: {}".format(e))
    sys.exit(-1)

def is_banned(resource):
    for banned in banned_extensions.split(','):
        if banned in resource.split('/')[-1]:
            return True
    return False

def is_ubanned(resource):
    if not '.' in resource.split('/')[-1]:
        return True
    for unbanned in unbanned_extensions.split(','):
        if unbanned in resource.split('/')[-1]:
            return True
    return False

def size_is_banned(size):
    if str(size) in size_filter.split(','):
        return True
    return False

def table():
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

        if banned_extensions and is_banned(resource):
            continue

        if unbanned_extensions and not is_ubanned(resource):
            continue

        if size_filter and size_is_banned(response_size):
            continue

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
def tree():
    if not LeftAligned:
        print("asciitree not installed!")
        sys.exit(-1)

    tr = LeftAligned()
    tree = {'/': {}}

    def _put_into_dict(root, resource):
        resource = resource.decode('UTF-8', 'replace')
        component = resource.split('/')[0]
        if not component:
            return
        if not component in root.keys():
            root[component] = {}
        resource = "/".join(resource.split('/')[1:])
        _put_into_dict(root[component], resource=resource)

    for entry in data:
        (resource, code, ext, response_size) = (entry[3], entry[5], entry[4], entry[6])

        if banned_extensions and is_banned(resource):
            continue

        if unbanned_extensions and not is_ubanned(resource):
            continue

        if size_filter and size_is_banned(response_size):
            continue
        if code in response_codes:
            if ext:
                resource = resource + ext
            _put_into_dict(tree['/'], resource)

    print(tr(tree))

if __name__ == '__main__':
    if args.tree:
        tree()
    else:
        table()
