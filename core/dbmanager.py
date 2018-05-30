import sqlite3
import time
import os
import sys

try:
    import Queue
except:
    import queue as Queue

from core.printer import Console

OUTPUT_DIR = "output" + os.sep
SUFIX = ".sqlite"


class DBManager():
    def __init__(self, database_name):

        # Check for self.database_path, create dirs and database if they don't exists
        self.database_path = OUTPUT_DIR + database_name + SUFIX
        if not os.path.isfile(self.database_path):
            if not os.path.isdir(OUTPUT_DIR):
                os.mkdir(OUTPUT_DIR)
            try:
                connection = sqlite3.connect(self.database_path)
                connection.text_factory = str
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

            except Exception as e:
                print("[DBManager] Error creating database {0}").format(database_name)
                sys.exit()

        self.dead = False
        self.queue = Queue.Queue()
        self.database_name = database_name

    def get_a_task(self, alived):
        try:
            task = self.queue.get(False)
            if task:
                self.process(task)
                self.queue.task_done()
                Console.body(task)
            else:
                print("no task")
            return True
        except Queue.Empty:
            return bool(alived)

    def get_results_queue(self):
        return self.queue

    def process(self, task):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()
        connection.text_factory = str
        # Check if the record already exists
        record = {"url": task.target, "resource": task.resource, "extension": task.extension,
                  "response_code": task.response_code}
        try:
            cursor.execute("SELECT * FROM requests WHERE \
                            url=:url AND \
                            resource=:resource AND \
                            extension=:extension AND \
                            response_code=:response_code", record)
        except Exception as e:
            print(e)
        # TODO banned response code at user will
        if not cursor.fetchone():
            if not task.response_code == "404":
                if task.is_valid():
                    cursor.execute("INSERT INTO requests VALUES (?,?,?,?,?,?,?,?,?,?)", task.values() + (time.time(),))
                    connection.commit()
        connection.close()
