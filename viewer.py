import sys
import sqlite3
import os

PREFIX = "data" + os.sep
QUERY = "SELECT * FROM requests ORDER BY resource"

class Item
    def __init__(self):
        self.url
        self.resource
        self.extension
        self.response_code
        self.location

try:
    project_name = sys.argv[1]
except:
    print("Need a project sqlite file as argument")
    sys.exit()

connection = None
try:
    connection = sqlite3.connect(PREFIX + project_name)
except:
    print("Error opening database %s" PREFIX + project_name)

cursor = None
try:
    cursor = connection.cursor()
    cursor.execute(QUERY)


header = "<html><title>" + project_name + "</title>"



footer = "</html>"