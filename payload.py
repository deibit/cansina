import Queue

import Task

class Payload:
    def __init__(self, payload_filename, extensions = []):
        self.queue = Queue.Queue()
        self.extensions = extensions
        self.payload = ""
        with open(payload_filename) as payload:
            self.payload = payload.readlines()
