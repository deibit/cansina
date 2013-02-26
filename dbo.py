import sqlite3
import threading
import time
import os
import Queue

PREFIX = "data" + os.sep
SUFIX = ".sqlite"
SLEEP_TIME = 1

class DBManager(threading.Thread):

    def __init__(self, database_name, queue):
        threading.Thread.__init__(self)
        if not os.path.isfile(PREFIX + database_name + SUFIX):
            connection = sqlite3.connect(PREFIX + database_name + SUFIX)
            try:
                cursor = connection.cursor()
                cursor.execute("CREATE TABLE requests (\
                                payload TEXT,\
                                url TEXT,\
                                resource TEXT,\
                                extension TEXT,\
                                response_code TEXT,\
                                response_size INTEGER,\
                                response_time INTEGER,\
                                timestamp INTEGER);")
                connection.commit()
                connection.close()
            except:
                print "Error creating database"
                sys.exit()
        self.queue = queue
        self.database_name = database_name

    def run(self):
        while 1:
            if self.queue.empty():
                time.sleep(SLEEP_TIME)
            else:
                task = self.queue.get()
                if task.target == 'STOP':
                    self.queue.task_done()
                    break
                else:
                    self.process(task)
                    self.queue.task_done()

    def process(self, task):
        connection = sqlite3.connect(PREFIX + self.database_name + SUFIX)
        cursor = connection.cursor()
        # Check if the record already exists
        cursor.execute("SELECT * FROM requests WHERE \
                        url=:url AND \
                        resource=:resource AND \
                        extension=:extension AND \
                        response_code=:response_code",
                        {"url" : task.target,
                         "resource" : task.resource,
                         "extension" : task.extension,
                         "response_code" : task.response_code
                         })
        # TODO banned response code at user will
        if not cursor.fetchone():
            if not task.response_code == 404:
                cursor.execute("INSERT INTO requests VALUES (?,?,?,?,?,?,?,?)", \
                    task.to_database() + (time.time(),))
                connection.commit()
        connection.close()



