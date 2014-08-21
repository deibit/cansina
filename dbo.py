import sqlite3
import threading
import Queue
import time
import os
import sys

from printer import Console

PREFIX = "data" + os.sep
SUFIX = ".sqlite"
SLEEP_TIME = 0.1


class DBManager(threading.Thread):
    def __init__(self, database_name):
        self.dead = False
        threading.Thread.__init__(self)
        if not os.path.isfile(PREFIX + database_name + SUFIX):
            if not os.path.isdir('data'):
                os.mkdir('data')
            try:
                connection = sqlite3.connect(PREFIX + database_name + SUFIX)
                cursor = connection.cursor()
                cursor.execute("CREATE TABLE requests (\
                                line_number INTEGER, \
                                payload TEXT,\
                                url TEXT,\
                                resource TEXT,\
                                extension TEXT,\
                                response_code TEXT,\
                                response_size INTEGER,\
                                response_time INTEGER,\
                                location TEXT, \
                                t_stamp INTEGER);")
                connection.commit()
                connection.close()
            except:
                print "Error creating database"
                sys.exit()
        self.queue = Queue.Queue()
        self.database_name = database_name

    def get_results_queue(self):
        return self.queue

    def run(self):
        Console.header()
        while not self.dead or self.queue.not_empty:
            if self.queue.empty():
                time.sleep(SLEEP_TIME)
            else:
                task = self.queue.get()
                self.process(task)
                self.queue.task_done()
                Console.body(task)

    def process(self, task):
        connection = sqlite3.connect(PREFIX + self.database_name + SUFIX)
        cursor = connection.cursor()
        # Check if the record already exists
        record = {"url": task.target, "resource": task.resource, "extension": task.extension,
                  "response_code": task.response_code}
        cursor.execute("SELECT * FROM requests WHERE \
                        url=:url AND \
                        resource=:resource AND \
                        extension=:extension AND \
                        response_code=:response_code", record)
        # TODO banned response code at user will
        if not cursor.fetchone():
            if not task.response_code == "404":
                if task.is_valid():
                    cursor.execute("INSERT INTO requests VALUES (?,?,?,?,?,?,?,?,?,?)", task.values() + (time.time(),))
                    connection.commit()
        connection.close()

