import Queue

import task

class Payload(Queue.Queue):
    def __init__(self, payload_filename, extensions = []):
        self.extensions = extensions
        self.payload = ""
        with open(payload_filename) as payload:
            self.payload = payload.readlines()
        for n in self.payload:
            self.put(n)
