#!/usr/bin/env python
import sys
import sqlite3
import argparse
import urllib.parse as urlparse

try:
    from asciitree import LeftAligned
except:
    print("install asciitree for viewer feature")


RED = "\033[31m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
LBLUE = "\033[36m"
ENDC = "\033[0m"

colors = {"200": GREEN, "302": BLUE, "403": RED, "500": YELLOW}

response_codes = ["200"]

QUERY = "SELECT * FROM requests ORDER BY resource"


def viewer(project_name):
    try:
        with sqlite3.connect(project_name) as connection:
            cursor = connection.cursor()
            connection.text_factory = str
            cursor.execute(QUERY)
            data = cursor.fetchall()
            tree(data)

    except Exception as e:
        import traceback

        traceback.print_exc()
        print("Error opening database {}".format(project_name))
        print("Details: {}".format(e))
        sys.exit(-1)


def table(data):
    def comparator(a, b):
        if a.count("/") < b.count("/"):
            return -1
        if a.count("/") > b.count("/"):
            return 1
        if a.count("/") == b.count("/"):
            return 0

    # if used_payloads:
    #     output = {}
    #     for k, v in data:
    #         if not output.has_key(k):
    #             output[k] = [v]
    #             continue
    #         output[k].append(v)
    #     for k in output.keys():
    #         print("{}{}:".format(GREEN, k))
    #         output[k].sort()
    #         for v in set(output[k]):
    #             print("        {}{}".format(BLUE, v))
    #     sys.exit()

    data.sort(cmp=comparator, key=lambda x: x[2] + x[3] + x[4])
    for line in data:
        (url, resource, extension, response_code, location, response_size) = (
            line[2],
            line[3],
            line[4],
            line[5],
            line[8],
            line[6],
        )

        if response_code in response_codes:
            url = urlparse.urlparse(url)
            if not location:
                print(
                    "{}{} {:>8}: {}{}{}".format(
                        colors[response_code],
                        response_code,
                        response_size,
                        url.path,
                        resource,
                        extension,
                    )
                )
            else:
                print(
                    "{}{} {:>8}: {}{}{} -> {}".format(
                        colors[response_code],
                        response_code,
                        response_size,
                        url.path,
                        resource,
                        extension,
                        location,
                    )
                )


def tree(data):
    if not LeftAligned:
        print("asciitree not installed!")
        sys.exit(-1)

    tr = LeftAligned()
    tree = {"/": {}}

    def _put_into_dict(root, resource):
        resource = resource
        component = resource.split("/")[0]
        if not component:
            return
        if not component in root.keys():
            root[component] = {}
        resource = "/".join(resource.split("/")[1:])
        _put_into_dict(root[component], resource=resource)

    for entry in data:
        (resource, code, ext, response_size) = (entry[3], entry[5], entry[4], entry[6])
        if code in response_codes:
            if ext:
                resource = resource + ext
            _put_into_dict(tree["/"], resource)
    print(tr(tree))
