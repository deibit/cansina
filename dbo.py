import sqlite3
import threading
import time

PREFIX = "data" + os.sep

class Manager(threading.Thread):

    def __init__(self, database_name, queue):
        self.connection = sqlite3.connect(PREFIX + database_name)
        try:
            self.__create_database()
        except:
            print "Database %s exists, so continuing tasks" % database_name
        self.queue = queue

    def run(self):
        while not self.queue.empty():
            self.process(self.queue.get())
            self.queue.task_done()

    def process(self, task):
        cursor = self.connection.cursor()
        # Check if the record already exists
        cursor.execute("SELECT * FROM requests WHERE \
                        url=:url AND \
                        resource=:resource AND \
                        extension=:extension AND \
                        response_code=:response_code);",
            {   "url" : task.url,
                "resource" : task.resource,
                "extension" : task.extension,
                "response_code" : task.response_code
            })

        if not len(cursor.fetchone()) > 0:
            cursor.execute("INSERT INTO requests VALUES (?,?,?,?,?,?,?,?)", \
                task.to_database() + \
                time.time())
            connection.commit()

    def __create_database(self, database_name):
    ''' Creates a new database '''
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE requests (\
                        id INTEGER PRIMARY KEY ASC AUTOINCREMENT,\
                        payload, TEXT,\
                        url TEXT,\
                        resource TEXT,\
                        extension TEXT,\
                        response_code TEXT,\
                        response_size INTEGER,\
                        response_time INTEGER,\
                        timestamp INTEGER);")
        self.connection.commit()

    def __del__(self):
        self.connection.close()

