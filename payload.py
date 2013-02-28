import multiprocessing
from task import Task

class Payload():
    def __init__(self, target, payload_filename, extensions = [""]):
        self.queue = multiprocessing.JoinableQueue()
        self.payload = ""
        self.size = 0
        with open(payload_filename) as payload:
            self.payload = payload.readlines()
            self.size = len(self.payload)
        #
        # TODO support for multiple extensions via generators
        #
        for resource in self.payload:
            if not target[-1] == '/':
                target = target + '/'
            resource = resource.strip()
            if resource[0] == '/':
                resource = resource[1:]
            self.queue.put(Task(payload_filename, target, resource, extensions[0]))
