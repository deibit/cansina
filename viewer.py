#!/usr/bin/env python -B
import sys
import os
import sqlite3
import argparse
import webbrowser

parser = argparse.ArgumentParser()
parser.add_argument('-p', dest = 'project_name',
                    help = "path to sqlite3 project file",
                    required = True)
parser.add_argument('-b', dest = 'browser',
                    help = "Open a default browser with the project results",
                    action="store_true",
                    default=False)
args = parser.parse_args()
project_name = args.project_name
browser = args.browser

QUERY = "SELECT * FROM requests ORDER BY resource"

header =    '''<html>
                <head>
                    <script src="../assets/js/jquery-1.9.0.min.js" type="text/javascript"></script>
                    <script src="../assets/js/bootstrap.min.js" type="text/javascript"></script>
                    <link href="../assets/css/bootstrap.css" rel="stylesheet">
                    <link href="../assets/css/bootstrap.min.css" rel="stylesheet" media="screen">
                    <link href="../assets/css/bootstrap.min.css" rel="stylesheet" media="screen">

                </head>
            '''

body =      '''<body>
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Line</th>
                            <th>Payload</th>
                            <th>URL</th>
                            <th>Code</th>
                            <th>Size</th>
                            <th>Location</th>
                        </tr>
                    </thead>
            '''

footer = '</table></body></html>'

class Item:
    def __init__(self):
        self.linenumber = None
        self.payload_name = None
        self.url = None
        self.response_code = None
        self.size = None
        self.location = None

    def get_color(self):
        colors = {'200' : 'success',
                  '403' : 'error',
                  '401' : 'error',
                  '301' : 'info',
                  '302' : 'info',
                  '500' : 'warning'
                  }
        try:
            return colors[self.response_code]
        except:
            return ""

connection = None
try:
    connection = sqlite3.connect(project_name)
except:
    print("Error opening database " + project_name)
    sys.exit()

cursor = None
try:
    cursor = connection.cursor()
    cursor.execute(QUERY)
except:
    print("Error getting cursor in database " + project_name)
    sys.exit()

objects = []
data = cursor.fetchall()
connection.close()
for i in data:
    item = Item()
    item.linenumber = i[0]
    item.payload_name = i[1]
    item.url = i[2] + i[3] + i[4]
    item.response_code = i[5]
    item.size = i[6]
    item.location = i[8]
    objects.append(item)

project_html = project_name.replace(".sqlite", '') + ".html"
with open(project_html, 'w') as f:
    f.write(header + os.linesep)
    f.write(body + os.linesep)
    f.write('<tbody>' + os.linesep)
    for i in objects:
        f.write("<tr class='" + i.get_color() + "'>" + os.linesep)
        f.write("<td>" + str(i.linenumber) + "</td>" + os.linesep)
        f.write("<td>" + i.payload_name + "</td>" + os.linesep)
        f.write("<td><a href='" + i.url + "'>" + i.url + "</a></td>" + os.linesep)
        f.write("<td>" + i.response_code + "</td>" + os.linesep)
        f.write("<td>" + str(i.size) + "</td>" + os.linesep)
        f.write("<td>" + i.location + "</td>" + os.linesep)
        f.write("</tr>" + os.linesep)
    f.write('</tbody>' + os.linesep)
    f.write(footer + os.linesep)

if browser:
    webbrowser.open_new_tab("data/" + project_html)
