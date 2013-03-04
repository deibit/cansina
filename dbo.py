import sqlite3
import multiprocessing
import time
import os
import sys

PREFIX = "data" + os.sep
SUFIX = ".sqlite"
SLEEP_TIME = 0.5

class DBManager(multiprocessing.Process):

    def __init__(self, database_name, queue, payload_size):
        multiprocessing.Process.__init__(self)
        if not os.path.isfile(PREFIX + database_name + SUFIX):
            if not os.path.isdir('data'):
                os.mkdir('data')
            connection = sqlite3.connect(PREFIX + database_name + SUFIX)
            try:
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
                                timestamp INTEGER);")
                connection.commit()
                connection.close()
            except:
                print "Error creating database"
                sys.exit()
        self.queue = queue
        self.database_name = database_name
        self.payload_size = payload_size

    def run(self):
        counter = 0
        print("-------------------------------")
        print(" %    CODE        SIZE    URL  ")
        print("-------------------------------")
        while 1:
            if self.queue.empty():
                time.sleep(SLEEP_TIME)
            else:
                task = self.queue.get()
                counter = counter + 1
                if task.target == 'STOP':
                    self.queue.task_done()
                    break
                else:
                    self.process(task)
                    self.queue.task_done()

                    #
                    # Terminal workout
                    #
                    percentage = counter * 100 / self.payload_size
                    target = task.get_complete_target()
                    if len(target) > 80:
                        target = target[:80] + '...(etc)'
                    linesep = ""
                    if task.is_valid():
                        linesep = os.linesep
                    to_console = "{0:3}%  {1:^6} {2:10}    {3}".format(percentage,
                                                                task.response_code,
                                                                task.response_size,
                                                                target)
                    sys.stdout.write(to_console + linesep)
                    sys.stdout.flush()
                    time.sleep(0.1)
                    sys.stdout.write('\r')
                    sys.stdout.write ("\x1b[0K")
                    sys.stdout.flush()

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
            if not task.response_code == "404":
                if task.is_valid():
                    cursor.execute("INSERT INTO requests VALUES (?,?,?,?,?,?,?,?,?)", \
                        task.values() + (time.time(),))
                    connection.commit()
        connection.close()

        def terminate(self):
            print "DB process %s terminated" % self.pid
            multiprocessing.Process.terminate(self)



